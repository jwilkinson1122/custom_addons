import logging
import json
from odoo import api, fields, models, http, _
from odoo.exceptions import UserError
from odoo.http import request, route

from ..helpers.summary_helper import render_summary_html, compute_cpq_price_breakdown
from ..helpers.qr_helper import parse_cpq_qr_payload

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

        # 🛠️ Force create variant if missing:
        if not template.product_variant_id:
            variant = request.env['product.product'].sudo().create({
                'product_tmpl_id': template.id,
            })
            _logger.info("🟢 Created missing variant ID %s for template %s", variant.id, template.id)

        ptal_ids = []
        for ptal in template.valid_product_template_attribute_line_ids:
            ptal_data = {
                'id': ptal.id,
                'name': ptal.attribute_id.display_name,
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
                'product_variant_id': [template.product_variant_id.id],  # ✅ Always valid now!
                'uom_id': [template.uom_id.id] if template.uom_id else [],
            },
            'ptal_ids': ptal_ids,
        }

    @route('/cpq/<int:product_tmpl_id>/validate', type='json', auth='user')
    def cpq_validate(self, product_tmpl_id, combination):

        _logger.info("🔍 Flattened combination received for validation: %s", combination)

        template = request.env['product.template'].sudo().browse(product_tmpl_id)
        if not template or not template.cpq_ok:
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

        line = request.env['sale.order.line'].sudo().browse(active_id)
        # line = request.env["sale.order.line"].browse(line_id)
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
        price_unit = breakdown["final_price"] / breakdown["quantity"]
        product_uom_qty = breakdown["quantity"]

        # line.write({
        #     'cpq_configuration_json': config_json,
        #     'cpq_configuration_summary': summary_html,
        #     'product_uom_qty': configuration.get("quantity_to_make", 1),
        #     'name': configuration.get("name") or line.name,
        # })

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
        }

    @route('/cpq/<int:product_tmpl_id>/price_preview', type='json', auth='user')
    def cpq_price_preview(self, product_tmpl_id, configuration, context=None):
        env = request.env
        ctx = dict(context or {}, **request.context)

        order_id = ctx.get("active_sale_order_id")
        if not order_id:
            return {"error": "Missing order context."}

        order_line = env['sale.order.line'].with_context(ctx).new({
            'order_id': order_id,
            'product_template_id': product_tmpl_id,
        })

        result = compute_cpq_price_breakdown(env, order_line, configuration)

        return {
            "price": result["final_price"],
            "breakdown": result,
        }

class CPQScanController(http.Controller):

    @route('/cpq/scan_qr', type='json', auth='user')
    def scan_qr_code(self, qr_data, **kw):
        """
        Receive QR scan payload, parse the QR content,
        and fetch the related sale order and order line.
        """
        try:
            parsed = parse_cpq_qr_payload(qr_data)
            _logger.info("🟢 [CPQ QR] Parsed QR Data: %s", parsed)

            if not parsed.get('order_id'):
                return {'error': _("Missing order ID in QR data.")}

            order = request.env['sale.order'].sudo().browse(parsed['order_id'])
            if not order.exists():
                return {'error': _("Sale Order not found for ID %s") % parsed['order_id']}

            result = {
                'order_id': order.id,
                'order_name': order.name,
                'order_partner': order.partner_id.display_name,
            }

            if parsed.get('line_id'):
                line = request.env['sale.order.line'].sudo().browse(parsed['line_id'])
                if line.exists():
                    result['line_id'] = line.id
                    result['line_name'] = line.name
                    result['config_hash'] = parsed.get('config_hash')

            return result

        except Exception as e:
            _logger.exception("❌ Error processing CPQ QR scan:")
            return {'error': _('An unexpected error occurred while processing the QR scan.')}

    @route('/cpq/qr_scan', type='json', auth='user')
    def cpq_qr_scan(self, payload, status=None, **kwargs):
        """
        Handle the incoming QR scan event.
        Expects:
            - payload: the URI-style QR data
            - status: 'scan-in' or 'scan-out'
        """
        _logger.info(f"📥 CPQ QR scan received: payload={payload}, status={status}")

        try:
            parsed = parse_cpq_qr_payload(payload)
            order_id, line_id = parsed.get('order_id'), parsed.get('line_id')

            if not order_id or not line_id:
                raise UserError(_("Incomplete QR data. Order ID and Line ID are required."))

            order_line = request.env['sale.order.line'].sudo().browse(line_id)
            if not order_line.exists():
                return {'error': 'Sale order line not found.'}

            order_line.message_post(body=f"🔄 {status or 'scanned'} by {request.env.user.name}")

            return {'success': True, 'order_id': order_id, 'line_id': line_id, 'status': status}

        except Exception as e:
            _logger.exception("❌ Error in QR scan event handler:")
            return {'error': _('Failed to process QR scan event.')}

