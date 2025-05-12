import logging
import json
from odoo import api, fields, models, http, _, SUPERUSER_ID
from odoo.models import NewId
from odoo.exceptions import UserError
from odoo.http import request, route
from ..helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown, sanitize_for_json, get_cpq_config_dict, rebuild_selected_dict, generate_virtual_ptavs_from_cpq
from ..hooks import check_cpq_value_links, repair_cpq_attribute_links

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(http.Controller):

    def _cpq_extract_from_combination(self, product_tmpl, combination):
        _logger.info("[_cpq_extract_from_combination] Starting extraction:\n%s", json.dumps(combination, indent=2))
        
        cpq_val_model = request.env["cpq.attribute.value"].sudo()
        pav_model = request.env["product.attribute.value"].sudo()

        ptav_ids = []
        custom_dict = {}

        # 🔄 Flatten left/right or selected structures
        if isinstance(combination.get("left"), dict) or isinstance(combination.get("right"), dict):
            flat_combination = {**combination.get("left", {}), **combination.get("right", {})}
            _logger.debug("Detected bilateral config. Flattened keys: %s", list(flat_combination.keys()))
        elif isinstance(combination.get("selected"), dict):
            flat_combination = combination["selected"]
            _logger.debug("Using 'selected' key with keys: %s", list(flat_combination.keys()))
        else:
            flat_combination = combination
            _logger.debug("Using flat config keys: %s", list(flat_combination.keys()))

        _logger.info("➡️ %d attribute keys to resolve", len(flat_combination))

        for key, val in flat_combination.items():
            try:
                cpq_val_id = int(key)
            except ValueError:
                _logger.warning("Skipping non-integer key: %s", key)
                continue

            if pav_model.browse(cpq_val_id).exists():
                _logger.warning("Skipping legacy PAV ID %s (still active)", cpq_val_id)
                continue

            # ✅ Existing PTAV?
            ptav = request.env["product.template.attribute.value"].sudo().browse(cpq_val_id)
            if ptav.exists() and ptav.product_tmpl_id.id == product_tmpl.id:
                _logger.info("✔️ Using existing PTAV: %s (ID %s)", ptav.display_name, ptav.id)
                ptav_ids.append(ptav)
                if ptav.is_custom:
                    custom_value = val.get("value") if isinstance(val, dict) else val
                    custom_dict[ptav] = custom_value
                continue

        # 🔧 Fallback: generate missing virtuals
        cpq_value_ids = cpq_val_model.browse([int(k) for k in flat_combination if str(k).isdigit()])
        virtual_ptavs = generate_virtual_ptavs_from_cpq(request.env, product_tmpl, cpq_value_ids)
        ptav_ids += list(virtual_ptavs)

        # 🔍 Log final PTAVs
        for ptav in ptav_ids:
            safe_id = getattr(ptav, 'x_virtual_cpq_id', '—')
            safe_name = ptav.name or '(Unnamed)'
            _logger.debug("🧪 Final PTAV: attr=%s | name=%s | id=%s | price=%.2f",
                        ptav.attribute_id.name, safe_name, safe_id, ptav.price_extra)

        if not ptav_ids:
            _logger.warning("🚫 No PTAVs resolved")

        return request.env["product.template.attribute.value"].concat(*ptav_ids), custom_dict

    def _flatten_combination_ids(self, combination):
        """
        Flattens a combination dictionary to extract all potential numeric value IDs.
        Supports bilateral format (left/right) and flattened single-sided configs.
        """
        _logger.debug("[_flatten_combination_ids] Flattening combination: %s", combination)

        ids = []

        # 1️⃣ Check for bilateral structure
        for side in ("left", "right"):
            side_vals = combination.get(side)
            if isinstance(side_vals, dict):
                keys = side_vals.keys()
                _logger.debug("🔎 Extracting from '%s': %s", side, list(keys))
                ids.extend(keys)

        # 2️⃣ Fallback to 'selected' or flat structure
        if not ids:
            if isinstance(combination.get("selected"), dict):
                selected_keys = combination["selected"].keys()
                _logger.debug("🔎 Extracting from 'selected': %s", list(selected_keys))
                ids.extend(selected_keys)
            else:
                keys = combination.keys()
                _logger.debug("🔎 Using top-level keys: %s", list(keys))
                ids.extend(keys)

        _logger.info("🧾 Flattened combination IDs: %s", list(ids))
        return list(ids)

    def _safe_int_keys(self, data):
        """
        Filters the flattened combination keys to include only valid integers.
        Logs and excludes bad keys like 'name', 'price_unit', etc.
        """
        raw_keys = self._flatten_combination_ids(data)
        good_keys = []
        bad_keys = []

        for k in raw_keys:
            if str(k).isdigit():
                good_keys.append(int(k))
            else:
                bad_keys.append(k)

        if bad_keys:
            _logger.warning("[CPQ] Skipping non-integer keys during value ID parsing: %s", bad_keys)

        _logger.info("✅ Valid numeric keys for extraction: %s", good_keys)
        return good_keys

    def _get_validated_and_original_selected(self, template, config_dict):
        """
        Validates a config dict's selected keys and returns:
        - ptav_ids
        - custom_dict
        - original_selected (possibly rebuilt)
        - sanitized_selected (used only for validation)
        """
        original_selected = dict(config_dict.get("selected", {}))

        # Rebuild if empty
        if not original_selected:
            original_selected = rebuild_selected_dict(config_dict)
            _logger.warning("[CPQ] 'selected' missing — rebuilt from flat config.")

        ptav_ids, custom_dict = self._cpq_extract_from_combination(template, original_selected)

        # valid_ptav_ids = {str(p.id) for p in ptav_ids if p.id}

        valid_ptav_ids = {
            ptav.x_virtual_cpq_id or str(ptav.id)
            for ptav in ptav_ids
            if ptav.x_virtual_cpq_id or ptav.id
        }
        sanitized_selected = {
            k: v for k, v in original_selected.items() if str(k) in valid_ptav_ids
        }
        removed_keys = set(original_selected.keys()) - set(sanitized_selected.keys())
        if removed_keys:
            _logger.warning("[CPQ] Removed orphaned keys from selected: %s", removed_keys)

        return ptav_ids, custom_dict, original_selected, sanitized_selected

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
        _logger.debug("Context received: %s", json.dumps(context, indent=2))

        active_model = context.get("active_model")
        active_id = context.get("active_id")
        if active_model != "sale.order.line" or not active_id:
            raise UserError(_("Invalid active model or active ID."))

        line = request.env["sale.order.line"].browse(active_id)
        if not line.exists():
            raise UserError(_("Sale order line not found."))

        config_dict = get_cpq_config_dict(configuration)
        template = line.product_template_id

        # 🔍 Extract and validate
        ptav_ids, custom_dict, original_selected, _ = self._get_validated_and_original_selected(template, config_dict)

        # ✅ Validate only the sanitized config
        with request.env.cr.savepoint():
            valid, errors = template.with_context(allow_virtual_ptavs=True)._cpq_ensure_valid_values(
                ptav_ids, custom_dict, validate_only=True)
            if not valid:
                raise UserError("\n".join(errors.values()))

        # ✅ Use full original config (virtuals included) for pricing and saving
        config_dict["selected"] = original_selected
        config_json = json.dumps(config_dict)

        # 🔄 Re-browse the real ORM record
        line = request.env["sale.order.line"].sudo().browse(line.id)
        _logger.debug("🧪 Re-browsed line before summary: %s (ID: %s)", line, line.id)

        summary_html = render_summary_html(request.env, line, config_dict)
        breakdown = compute_cpq_price_breakdown(request.env, line, config_dict)
        quantity = breakdown.get("quantity") or 1.0
        price_unit = breakdown.get("final_price", 0.0) / quantity

        line.write({
            'cpq_configuration_json': config_json,
            'cpq_configuration_summary': summary_html,
            'product_uom_qty': quantity,
            'price_unit': price_unit,
            'name': config_dict.get("name") or line.name,
        })

        return sanitize_for_json({
            'configuration': config_dict,
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

        def serialize_attribute(attr):
            """Recursively serialize a cpq.attribute."""
            return {
                "id": attr.id,
                "name": attr.name,
                "is_group": attr.is_group,
                "display_type": attr.display_type,
                "required": attr.required,
                "sequence": attr.sequence,
                "values": [] if attr.is_group else [
                    {
                        "id": val.id,
                        "name": val.name,
                        "price_extra": val.price_extra,
                        "triggers": [child.id for child in val.triggers_child_attribute_ids],
                        "children": [],  # Reserved for future nested value logic
                    }
                    for val in attr.value_ids.filtered(lambda v: v.active)
                ],
                "children": [
                    serialize_attribute(child)
                    for child in attr.child_ids.filtered(lambda c: c.active)
                ] if attr.is_group else [],
            }

        root_attrs = template.cpq_root_attribute_ids.filtered(lambda a: a.active)
        result = [serialize_attribute(attr) for attr in root_attrs]

        # ✅ Log the tree output (dev only)
        _logger.info("🌳 [CPQ] Serialized attribute tree for template %s:\n%s", template.id, result)

        return result

    # @http.route('/cpq/attribute/tree/<int:product_template_id>', type='json', auth='user')
    # def cpq_attribute_tree(self, product_template_id):
    #     template = request.env['product.template'].sudo().browse(product_template_id)
    #     if not template.exists():
    #         raise UserError("Product template not found.")

    #     ptal_ids = []

    #     root_attrs = template.cpq_root_attribute_ids.filtered(lambda a: a.active)

    #     for group in root_attrs:
    #         ptal_ids.append({
    #             "id": group.id,
    #             "name": group.name,
    #             "is_group": True,
    #             "sequence": group.sequence,
    #         })

    #         for attr in group.child_ids.filtered(lambda a: a.active and not a.is_group):
    #             attr_data = {
    #                 "id": attr.id,
    #                 "name": attr.name,
    #                 "is_group": False,
    #                 "display_type": attr.display_type,
    #                 "required": attr.required,
    #                 "sequence": attr.sequence,
    #                 "values": [],
    #             }

    #             for val in attr.value_ids.filtered(lambda v: v.active):
    #                 attr_data["values"].append({
    #                     "id": val.id,
    #                     "name": val.name,
    #                     "price_extra": val.price_extra,
    #                     "triggers": [a.id for a in val.triggers_child_attribute_ids],
    #                     "children": [],  
    #                 })

    #             ptal_ids.append(attr_data)

    #     return ptal_ids

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

