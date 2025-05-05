import logging
import json
from odoo import api, fields, models, http, _
from odoo.exceptions import UserError
from odoo.http import request, route

from ..helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown
# from odoo.addons.cpq.helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(http.Controller):

    def _cpq_extract_from_combination(self, product_tmpl, combination):
        ptav_ids = request.env["product.template.attribute.value"].sudo()
        custom_dict = {}

        valid_ptav_ids = product_tmpl.valid_product_template_attribute_line_ids.mapped("product_template_value_ids")
        valid_ids_set = set(valid_ptav_ids.ids)

        # Handle bilateral (left/right)
        if any(side in combination for side in ("left", "right")):
            flat_combination = {}
            for side in ("left", "right"):
                side_vals = combination.get(side)
                if isinstance(side_vals, dict):
                    flat_combination.update(side_vals)
        else:
            flat_combination = combination

        for key, val in flat_combination.items():
            try:
                ptav_id_int = int(key)
            except ValueError:
                continue

            if ptav_id_int not in valid_ids_set:
                continue

            ptav_id = valid_ptav_ids.filtered(lambda p: p.id == ptav_id_int)
            if not ptav_id:
                continue

            ptav_ids |= ptav_id
            if ptav_id.is_custom:
                custom_dict[ptav_id] = val

        return ptav_ids, custom_dict

    @route('/cpq_product_configurator/<int:product_tmpl_id>/data', type='json', auth='user')
    def load_data(self, product_tmpl_id, **kwargs):
        _logger.info("🧩 [CPQ] Load data for template ID %s", product_tmpl_id)
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

    @route('/cpq/<int:product_tmpl_id>/validate', type='json', auth='user')
    def cpq_validate(self, product_tmpl_id, combination):

        _logger.info("🔍 Flattened combination received for validation: %s", combination)

        template = request.env['product.template'].sudo().browse(product_tmpl_id)
        if not template.exists() or not template.cpq_ok:
            return {"valid": False, "errors": {"general": _("Invalid CPQ product.")}}
        
        # _logger.info("🔍 Flattened combination received for validation: %s", combination)
        ptav_ids, custom_dict = self._cpq_extract_from_combination(template, combination)
        valid, msg = template._cpq_ensure_valid_values(
            ptav_ids, custom_dict, raise_on_invalidity=False, validate_only=True
        )

        return {
            "valid": valid,
            "errors": msg or {},
        }

    @route('/cpq_product_configurator/<int:product_tmpl_id>/configure', type='json', auth='user')
    def configure(self, product_tmpl_id, configuration=None, **kwargs):
        _logger.info("🧩 [CPQ] Configure called for template ID %s", product_tmpl_id)
        _logger.debug("📦 Config payload: %s", json.dumps(configuration, indent=2))

        context = request.params.get("context") or {}
        active_model = context.get("active_model")
        active_id = context.get("active_id")

        _logger.debug("🧩 Context received: %s", json.dumps(context, indent=2))


        if active_model != "sale.order.line" or not active_id:
            _logger.error("❌ Invalid active model or active ID: %s", context)
            raise UserError(_("Invalid active model or active ID."))

        # line = request.env['sale.order.line'].sudo().browse(active_id)
        line = request.env["sale.order.line"].browse(active_id)
        if not line.exists():
            _logger.error("❌ Sale order line not found for ID %s", active_id)
            raise UserError(_("Sale order line not found."))
        try:
            config_json = json.dumps(configuration)
        except Exception as e:
            _logger.exception("❌ Failed to serialize configuration:")
            raise UserError(_("Configuration could not be saved. Please check your selections."))


        summary_html = render_summary_html(request.env, line, configuration)
        
        # ✅ Compute correct price breakdown
        breakdown = compute_cpq_price_breakdown(request.env, line, configuration)
        # price_unit = breakdown["final_price"] / breakdown["quantity"]
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

        _logger.info("✅ Configuration saved to line %s", line.id)

        return {
            'configuration': configuration,
            'sale_order_line_id': line.id,
            'sale_order_id': line.order_id.id,
            'price_breakdown': breakdown,  # 👈 optional if used in frontend
            'matrix_override': breakdown.get("from_matrix", False),  
        }

    @route('/cpq/<int:product_tmpl_id>/price_preview', type='json', auth='user')
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
        return {"price": result["final_price"], "breakdown": result}
    

class CPQAttributeController(http.Controller):

    @route('/cpq/attribute/tree/<int:product_template_id>', type='json', auth='user')
    def cpq_attribute_tree(self, product_template_id):
        template = request.env['product.template'].sudo().browse(product_template_id)
        if not template.exists():
            raise UserError("Product template not found.")

        root_attrs = template.cpq_root_attribute_ids.filtered(lambda a: a.active)
        return self._build_attribute_tree(root_attrs)

    def _build_attribute_tree(self, attrs, seen=None):
        seen = seen or set()
        result = []

        for attr in attrs:
            if attr.id in seen:
                continue  # Avoid cycles
            seen.add(attr.id)

            node = {
                "id": attr.id,
                "name": attr.name,
                "display_type": attr.display_type,
                "required": attr.required,
                "sequence": attr.sequence,
                "is_group": attr.is_group,
                "values": [],
            }

            if not attr.is_group:
                for val in attr.value_ids.filtered(lambda v: v.active):
                    children = self._build_attribute_tree(val.triggers_child_attribute_ids, seen)
                    node["values"].append({
                        "id": val.id,
                        "name": val.name,
                        "price_extra": val.price_extra,
                        "triggers": [a.id for a in val.triggers_child_attribute_ids],
                        "children": children,
                    })


            # for val in attr.value_ids.filtered(lambda v: v.active):
            #     children = self._build_attribute_tree(val.triggers_child_attribute_ids, seen)
            #     node["values"].append({
            #         "id": val.id,
            #         "name": val.name,
            #         "price_extra": val.price_extra,
            #         "triggers": [a.id for a in val.triggers_child_attribute_ids],
            #         "children": children,
            #     })

            result.append(node)
        return result


# Helper extension for attribute lines
# class ProductTemplateAttributeLine(models.Model):
#     _inherit = "product.template.attribute.line"

#     def _cpq_get_combination_info_list(self):
#         return [line._cpq_get_combination_info() for line in self]


 