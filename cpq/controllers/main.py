import logging
import json
from odoo import api, fields, models, http, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.http import request, route
from ..helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown, sanitize_for_json
from ..hooks import check_cpq_value_links, repair_cpq_attribute_links

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(http.Controller):

    def _cpq_extract_from_combination(self, product_tmpl, combination):
        _logger.info("[_cpq_extract_from_combination] Starting extraction from combination: %s", json.dumps(combination, indent=2))

        ptav_ids = request.env["product.template.attribute.value"].sudo()
        custom_dict = {}

        # Flatten left/right if bilateral
        if any(side in combination for side in ("left", "right")):
            flat_combination = {}
            for side in ("left", "right"):
                side_vals = combination.get(side)
                if isinstance(side_vals, dict):
                    _logger.debug("Found %s side with %d values", side, len(side_vals))
                    flat_combination.update(side_vals)
        else:
            flat_combination = combination
            _logger.debug("Single-sided combination with %d values", len(flat_combination))

        for key, val in flat_combination.items():
            try:
                ptav_id_int = int(key)
            except ValueError:
                _logger.warning("Skipping non-numeric key: %s", key)
                continue

            _logger.debug("Resolving value ID: %s", ptav_id_int)

            # Skip legacy product.attribute.value
            if request.env["product.attribute.value"].sudo().browse(ptav_id_int).exists():
                _logger.warning("Legacy product.attribute.value ID %s detected — skipping.", ptav_id_int)
                continue

            # Try classic PTAV
            ptav_id = request.env["product.template.attribute.value"].sudo().browse(ptav_id_int)
            if ptav_id.exists():
                _logger.info("Found real PTAV: %s", ptav_id.display_name)
                ptav_ids |= ptav_id

                if ptav_id.is_custom:
                    # [OK] Support object: {id: ..., value: ...} or raw custom value
                    custom_value = val["value"] if isinstance(val, dict) and "value" in val else val
                    custom_dict[ptav_id] = custom_value
                    _logger.info("Custom value stored for PTAV %s: %s", ptav_id.id, custom_dict.get(ptav_id))

                continue

            # Try fallback: CPQ attribute value → generate virtual PTAV
            cpq_val = request.env["cpq.attribute.value"].sudo().browse(ptav_id_int)
            if cpq_val.exists():
                cpq_attr = cpq_val.attribute_id
                if not cpq_attr.exists():
                    _logger.warning("CPQ value %s (ID %s) missing attribute.", cpq_val.name, cpq_val.id)
                    continue

                linked_product_attr = cpq_attr.linked_product_attribute_id
                if not linked_product_attr.exists():
                    _logger.warning("CPQ attribute %s (ID %s) missing linked product.attribute.", cpq_attr.name, cpq_attr.id)
                    continue

                if cpq_val.linked_option_id and not cpq_val.linked_option_id.exists():
                    _logger.warning("CPQ value %s — linked product.attribute.value is missing.", cpq_val.name)
                    continue

                _logger.info("🪄 Creating virtual PTAV for CPQ value %s", cpq_val.name)
                virtual_ptav = request.env["product.template.attribute.value"].new({
                    "product_tmpl_id": product_tmpl.id,
                    "attribute_id": linked_product_attr.id,
                    "product_attribute_value_id": cpq_val.id,
                })
                ptav_ids += virtual_ptav

                if cpq_val.is_custom:
                    custom_value = val["value"] if isinstance(val, dict) and "value" in val else val
                    custom_dict[virtual_ptav] = custom_value
            else:
                _logger.warning("Value ID %s could not be resolved to PTAV or CPQ value", ptav_id_int)

        if not ptav_ids:
            _logger.warning("No valid PTAVs resolved from combination: %s", flat_combination)

        _logger.info("Final PTAV IDs: %s", [p.id or "virtual" for p in ptav_ids])
        _logger.info("Final custom dict keys: %s", [p.id or "virtual" for p in custom_dict.keys()])
        return ptav_ids, custom_dict

    def _flatten_combination_ids(self, combination):
        """Extract all value IDs (as strings or ints) from a possibly bilateral structure."""
        _logger.debug("[_flatten_combination_ids] Flattening combination: %s", combination)

        ids = []
        for side in ("left", "right"):
            side_vals = combination.get(side)
            if isinstance(side_vals, dict):
                _logger.debug("Extracting IDs from %s side: %s", side, list(side_vals.keys()))
                ids.extend(side_vals.keys())

        if not ids:
            _logger.debug("Using top-level keys (non-bilateral): %s", list(combination.keys()))
            ids.extend(combination.keys())

        _logger.info("Flattened combination IDs: %s", ids)
        return ids
    
    # def _safe_int_keys(self, data):
    #     keys = self._flatten_combination_ids(data)
    #     valid_keys = []
    #     invalid_keys = []
    #     for k in keys:
    #         if str(k).isdigit():
    #             valid_keys.append(int(k))
    #         else:
    #             invalid_keys.append(k)

    #     if invalid_keys:
    #         _logger.warning("[CPQ] Ignoring non-integer combination keys: %s", invalid_keys)

    #     return valid_keys
    
    def _safe_int_keys(self, data):
        bad_keys = [k for k in self._flatten_combination_ids(data) if not str(k).isdigit()]
        if bad_keys:
            _logger.warning("[CPQ] Skipping non-integer keys during value ID parsing: %s", bad_keys)
        return [int(k) for k in self._flatten_combination_ids(data) if str(k).isdigit()]


    @http.route('/cpq_product_configurator/<int:product_tmpl_id>/data', type='json', auth='user')
    def load_data(self, product_tmpl_id, **kwargs):
        _logger.info("[CPQ] Load data for template ID %s", product_tmpl_id)
        template = request.env['product.template'].sudo().browse(product_tmpl_id)
        if not template.exists():
            raise UserError(_("Product template not found."))

        ptal_ids = []
        for ptal in template.valid_product_template_attribute_line_ids:
            ptal_data = {
                'id': ptal.id,
                'name': ptal.attribute_id.display_name,
                # 'display_type': ptal.display_type or "radio",
                'display_type': ptal.attribute_id.display_type or "radio",
                'ptav_ids': [
                    {
                        'id': ptav.id,
                        'name': ptav.name,
                        'is_custom': ptav.is_custom,
                        'price_extra': ptav.price_extra,
                        'html_color': ptav.html_color or "",         
                        'cpq_custom_type': ptav.cpq_custom_type or "", 
                    }
                    for ptav in ptal.product_template_value_ids
                ],
            }
            ptal_ids.append(ptal_data)

        return {
            'product_tmpl_id': {
                'id': template.id,
                'display_name': template.display_name,
                'description_sale': template.description_sale,
                'list_price': template.list_price,
            },
            'ptal_ids': ptal_ids,
        }

    @http.route('/cpq/<int:product_tmpl_id>/validate', type='json', auth='user')
    def cpq_validate(self, product_tmpl_id, combination, **kwargs):
        context = {"allow_virtual_ptavs": True, **(kwargs.get("context") or {})}
        _logger.info("Incoming combination: %s", combination)
        _logger.info("Incoming context: %s", context)

        try:
            template = request.env["product.template"].browse(product_tmpl_id).sudo().with_context(context)

            if not template.exists() or not template.cpq_ok:
                return {"valid": False, "errors": {"general": _("Invalid CPQ product.")}}

            _logger.info("Resolved template: %s", template.display_name)

            ptav_ids, custom_dict = self._cpq_extract_from_combination(template, combination)
            _logger.info("🧪 After extract: ptav_ids=%s", [p.id for p in ptav_ids])
            _logger.info("🧪 After extract: cpq_values=%s", self._safe_int_keys(combination))
            _logger.info("🧪 Custom dict keys: %s", list(custom_dict.keys()))
      
            if not ptav_ids and template.cpq_ok:
                safe_keys = self._safe_int_keys(combination)
                _logger.warning("[Fallback] No PTAVs extracted — checking safe int keys: %s", safe_keys)
                if safe_keys:
                    cpq_value_ids = request.env["cpq.attribute.value"].browse(safe_keys)
                    _logger.info("[Fallback] Browsed CPQ values: %s", [v.id for v in cpq_value_ids])
                    ptav_ids = template._cpq_generate_virtual_ptavs(cpq_value_ids)
                    _logger.info("[Fallback] Generated virtual PTAVs: %s", [p.id or "virtual" for p in ptav_ids])
                else:
                    _logger.error("[Fallback] No valid CPQ value keys found — cannot generate PTAVs")
                
                if not ptav_ids:
                    raise UserError(_("This product could not be configured. No attribute values were selected."))


            # if not ptav_ids and template.cpq_ok:
            #     cpq_value_ids = request.env["cpq.attribute.value"].browse(self._safe_int_keys(combination))
            #     if cpq_value_ids:
            #         _logger.warning("[Fallback] No PTAVs extracted — generating virtual from %s", cpq_value_ids)
            #         ptav_ids = template._cpq_generate_virtual_ptavs(cpq_value_ids)
            #     else:
            #         _logger.error("[ERROR] No valid PTAVs or CPQ values — aborting validation")
            #         return {"valid": False, "errors": {"general": _("No valid attributes could be selected.")}}

            _logger.info("Resolved ptav_ids recordset: %s", ptav_ids)
            _logger.info("Extracted ptav_ids: %s", [p.id or "virtual" for p in ptav_ids])
            _logger.info("Custom dict: %s", custom_dict)
            _logger.info("[CPQ] Validating combination: %s", json.dumps(combination, indent=2))

            valid, msg = template._cpq_ensure_valid_values(
                ptav_ids,
                custom_dict,
                raise_on_invalidity=False,
                validate_only=True,
            )

            _logger.info("Validity: %s", valid)

            if isinstance(msg, dict):
                _logger.info("Validation errors: %s", msg)
            else:
                _logger.warning("Validation failed: %s", msg)

            if valid:
                _logger.info("Validation passed for CPQ template %s", template.display_name)

            return sanitize_for_json({
                "valid": valid,
                "errors": msg if isinstance(msg, dict) else {"general": msg or _("Unknown error.")},
            })

        except Exception as e:
            _logger.exception("CPQ validation failed due to server error:")
            return {
                "valid": False,
                "errors": {"general": f"Server error: {str(e)}"},
            }

    @http.route('/cpq_product_configurator/<int:product_tmpl_id>/configure', type='json', auth='user')
    def configure(self, product_tmpl_id, configuration=None, **kwargs):
        _logger.info("[CPQ] Configure called for template ID %s", product_tmpl_id)
        _logger.debug("Config payload: %s", json.dumps(configuration, indent=2))

        context = {"allow_virtual_ptavs": True, **(kwargs.get("context") or {})}
        active_model = context.get("active_model")
        active_id = context.get("active_id")

        _logger.debug("Context received: %s", json.dumps(context, indent=2))

        if active_model != "sale.order.line" or not active_id:
            _logger.error("Invalid active model or active ID: %s", context)
            raise UserError(_("Invalid active model or active ID."))

        line = request.env["sale.order.line"].browse(active_id)
        if not line.exists():
            _logger.error("Sale order line not found for ID %s", active_id)
            raise UserError(_("Sale order line not found."))

        try:
            config_json = json.dumps(configuration)
        except Exception as e:
            _logger.exception("Failed to serialize configuration:")
            raise UserError(_("Configuration could not be saved. Please check your selections."))

        template = line.product_template_id
        ptav_ids, custom_dict = self._cpq_extract_from_combination(template, configuration)
        _logger.info("🧪 After extract: ptav_ids=%s", [p.id for p in ptav_ids])
        _logger.info("🧪 After extract: cpq_values=%s", self._safe_int_keys(configuration))
        _logger.info("🧪 Custom dict keys: %s", list(custom_dict.keys()))


        if not ptav_ids and template.cpq_ok:
            safe_keys = self._safe_int_keys(configuration)
            _logger.warning("[Fallback] No PTAVs extracted — checking safe int keys: %s", safe_keys)
            if safe_keys:
                cpq_value_ids = request.env["cpq.attribute.value"].browse(safe_keys)
                _logger.info("[Fallback] Browsed CPQ values: %s", [v.id for v in cpq_value_ids])
                ptav_ids = template._cpq_generate_virtual_ptavs(cpq_value_ids)
                _logger.info("[Fallback] Generated virtual PTAVs: %s", [p.id or "virtual" for p in ptav_ids])
            else:
                _logger.error("[Fallback] No valid CPQ value keys found — cannot generate PTAVs")
            
            if not ptav_ids:
                raise UserError(_("This product could not be configured. No attribute values were selected."))


        # if not ptav_ids and template.cpq_ok:
        #     cpq_value_ids = request.env["cpq.attribute.value"].browse(self._safe_int_keys(configuration))
        #     if cpq_value_ids:
        #         _logger.warning("[Fallback] No PTAVs extracted — generating virtual from %s", cpq_value_ids)
        #         ptav_ids = template._cpq_generate_virtual_ptavs(cpq_value_ids)
        #     else:
        #         _logger.error("[ERROR] No valid PTAVs or CPQ values — aborting configure")
        #         raise UserError(_("This product could not be configured. No attribute values were selected."))

        with request.env.cr.savepoint():
            tmpl_with_context = template.with_context(allow_virtual_ptavs=True)
            valid, errors = tmpl_with_context._cpq_ensure_valid_values(ptav_ids, custom_dict, validate_only=True)
            if not valid:
                raise UserError("\n".join(errors.values()))

        summary_html = render_summary_html(request.env, line, configuration)
        breakdown = compute_cpq_price_breakdown(request.env, line, configuration)
        quantity = breakdown.get("quantity") or 1.0
        price_unit = breakdown.get("final_price", 0.0) / quantity
        product_uom_qty = breakdown["quantity"]

        line.write({
            'cpq_configuration_json': config_json,
            'cpq_configuration_summary': summary_html,
            'product_uom_qty': product_uom_qty,
            'price_unit': price_unit,
            'name': configuration.get("name") or line.name,
        })

        _logger.info("Configuration saved to line %s", line.id)

        return sanitize_for_json({
            'configuration': configuration,
            'sale_order_line_id': line.id,
            'sale_order_id': line.order_id.id,
            'price_breakdown': breakdown,
            'matrix_override': breakdown.get("from_matrix", False),
        })

    @http.route('/cpq/<int:product_tmpl_id>/price_preview', type='json', auth='user')
    def cpq_price_preview(self, product_tmpl_id, configuration, context=None):
        env = request.env
        ctx = dict(context or {}, **request.context)

        order_id = ctx.get("active_sale_order_id")
        if not order_id:
            _logger.warning("Missing order ID in context for price preview. Context: %s", ctx)
            return {
                "price": 0.0,
                "breakdown": {
                    "base_price": 0.0,
                    "discount_factor": 1.0,
                    "quantity": configuration.get("quantity_to_make", 1),
                    "laterality": configuration.get("laterality", "bilateral"),
                    "split": configuration.get("split", False),
                    "left": 0.0,
                    "right": 0.0,
                    "extras_total": 0.0,
                    "subtotal": 0.0,
                    "final_price": 0.0,
                    "total": 0.0,
                }
            }

        # if not order_id:
        #     return {"error": "Missing order context."}

        order_line = env['sale.order.line'].with_context(ctx).new({
            'order_id': order_id,
            'product_template_id': product_tmpl_id,
        })

        result = compute_cpq_price_breakdown(env, order_line, configuration)

        return sanitize_for_json({
            "price": result["final_price"],
            "breakdown": result
        })

        # return {"price": result["final_price"], "breakdown": result}
    

class CPQAttributeController(http.Controller):

    @http.route('/cpq/attribute/tree/<int:product_template_id>', type='json', auth='user')
    def cpq_attribute_tree(self, product_template_id):
        template = request.env['product.template'].sudo().browse(product_template_id)
        if not template.exists():
            raise UserError("Product template not found.")

        ptal_ids = []

        root_attrs = template.cpq_root_attribute_ids.filtered(lambda a: a.active)

        for group in root_attrs:
            ptal_ids.append({
                "id": group.id,
                "name": group.name,
                "is_group": True,
                "sequence": group.sequence,
            })

            for attr in group.child_ids.filtered(lambda a: a.active and not a.is_group):
                attr_data = {
                    "id": attr.id,
                    "name": attr.name,
                    "is_group": False,
                    "display_type": attr.display_type,
                    "required": attr.required,
                    "sequence": attr.sequence,
                    "values": [],
                }

                for val in attr.value_ids.filtered(lambda v: v.active):
                    attr_data["values"].append({
                        "id": val.id,
                        "name": val.name,
                        "price_extra": val.price_extra,
                        "triggers": [a.id for a in val.triggers_child_attribute_ids],
                        "children": [],  # Reserved for future nested support
                    })

                ptal_ids.append(attr_data)

        return ptal_ids

    @http.route("/cpq/dev/check_links", type="http", auth="user")
    def cpq_check_links(self):
        env = api.Environment(http.request.cr, SUPERUSER_ID, http.request.env.context)
        html = check_cpq_value_links(env)
        return http.Response(html, content_type='text/html')

    @http.route("/cpq/dev/repair_links", type="http", auth="user")
    def cpq_repair_links(self):
        env = api.Environment(http.request.cr, SUPERUSER_ID, http.request.env.context)
        result = repair_cpq_attribute_links(env)

        def list_to_html(label, values):
            if not values:
                return f"<p><b>{label}:</b> <span style='color:green'>None</span></p>"
            rows = ''.join(f"<li>{v}</li>" for v in values)
            return f"<p><b>{label}:</b></p><ul>{rows}</ul>"

        html = f"""
            <h2>CPQ Repair Complete:</h2>
            <p><b>Attributes fixed:</b> {len(result['attributes_fixed'])}</p>
            <p><b>Values created:</b> {len(result['values_created'])}</p>
            <p><b>Values skipped:</b> {len(result['values_skipped_existing'])}</p>
            {list_to_html("Attributes Fixed", result['attributes_fixed'])}
            {list_to_html("Values Created", result['values_created'])}
            {list_to_html("Values Skipped", result['values_skipped_existing'])}
            <br><a href="/web#menu_id=menu_cpq_repair_tools&model=ir.ui.menu">Back</a>
        """
        return http.Response(html, content_type='text/html')

