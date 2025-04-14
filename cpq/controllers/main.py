
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.http import Controller, request, route
from ..helpers.summary_helper import render_summary_html
# from odoo.addons.cpq.helpers.summary_helper import render_summary_html


import logging
import json

_logger = logging.getLogger(__name__)

class ProductConfiguratorController(Controller):

    def _cpq_extract_from_combination(self, product_tmpl_id, combination):
        ptav_ids = request.env["product.template.attribute.value"].sudo()
        custom_dict = {}

        valid_ptav_ids = product_tmpl_id.valid_product_template_attribute_line_ids.mapped("product_template_value_ids")
        valid_ids_set = set(valid_ptav_ids.ids)

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

            ptav_id = valid_ptav_ids.filtered(lambda ptav: ptav.id == ptav_id_int)
            if not ptav_id:
                continue

            ptav_id.ensure_one()
            ptav_ids |= ptav_id

            if ptav_id.is_custom:
                custom_dict[ptav_id] = val

        return ptav_ids, custom_dict

    @route("/cpq/<int:product_tmpl_id>/data", type="json", auth="user")
    def cpq_tmpl_data(self, product_tmpl_id, company_id=None, pricelist_id=None, ptav_ids=None):
        env = request.env
        product_tmpl = env["product.template"].sudo().browse(product_tmpl_id)

        if not product_tmpl.exists():
            raise UserError(_("Product template not found."))

        if not product_tmpl.cpq_ok:
            raise UserError(_("Not a CPQ enabled product!"))

        currency = env.user.company_id.currency_id
        pricelist = pricelist_id and env["product.pricelist"].browse(pricelist_id)

        currency_data = {
            "id": currency.id,
            "name": currency.name,
            "symbol": currency.symbol,
            "position": currency.position,
        }

        ptal_data = []
        for ptal in product_tmpl.valid_product_template_attribute_line_ids:
            attribute_data = {
                "id": ptal.id,
                "name": ptal.attribute_id.name,
                "display_type": ptal.attribute_id.display_type,
                "ptav_ids": [],
            }

            for ptav in ptal.product_template_value_ids:
                # Get price extra
                price_extra = (
                    pricelist._get_product_price_extra(
                        ptav,
                        currency=currency,
                        company=env.company,
                    )
                    if pricelist
                    else ptav.currency_id._convert(
                        ptav.price_extra,
                        currency,
                        env.company,
                        fields.Date.today(),
                    )
                )

                formatted_name = ptav.name
                if price_extra:
                    formatted_name += (
                        f" (+{currency.symbol}{price_extra:.2f})"
                        if currency.position == "before"
                        else f" (+{price_extra:.2f}{currency.symbol})"
                    )

                # ⚠️ Add side-specific pricing if applicable (for now, same price both sides)
                side_prices = {
                    "left": price_extra,
                    "right": price_extra,
                }

                attribute_data["ptav_ids"].append({
                    "id": ptav.id,
                    "name": ptav.name,
                    "formatted_name": formatted_name,
                    "is_custom": ptav.is_custom,
                    "price_extra": price_extra,
                    "side_prices": side_prices,
                })

            ptal_data.append(attribute_data)

        return {
            "product_tmpl_id": {
                "id": product_tmpl.id,
                "name": product_tmpl.name,
                "display_name": product_tmpl.display_name,
                "list_price": product_tmpl.list_price,
                "cpq_ref": product_tmpl.cpq_ref,
                "description_sale": product_tmpl.description_sale,
                "currency": currency_data,
            },
            "ptal_ids": ptal_data,
        }

    @route("/cpq/<int:product_tmpl_id>/validate", type="json", auth="user")
    def cpq_validate(self, product_tmpl_id, combination):
        product_tmpl_id = request.env["product.template"].sudo().browse(product_tmpl_id)
        if not product_tmpl_id.cpq_ok:
            return {"valid": False, "msg": _("Not CPQ Enabled!")}

        ptav_ids, custom_dict = self._cpq_extract_from_combination(product_tmpl_id, combination)
        variant_ok, msg = product_tmpl_id._cpq_ensure_valid_values(
            ptav_ids, custom_dict, raise_on_invalidity=False, validate_only=True
        )

        return {"valid": variant_ok, "errors": msg}
    

    @route('/cpq/<int:product_tmpl_id>/configure', type='json', auth='user')
    def cpq_configure(self, product_tmpl_id, configuration, **kwargs):
        env = request.env
        product_tmpl = env['product.template'].sudo().browse(product_tmpl_id)

        if not product_tmpl.exists():
            raise UserError(_('Product template not found.'))
        if not product_tmpl.cpq_ok:
            raise UserError(_('Not a CPQ enabled product!'))

        config = {
            'laterality': configuration.get('laterality', 'unspecified'),
            'name': configuration.get('name') or f"{product_tmpl.name} - {configuration.get('laterality', 'unspecified').capitalize()}",
            'selected': configuration.get('selected', {}),
            'split': configuration.get('split', False),
            'quantity_to_make': configuration.get('quantity_to_make', 1),
            'left_price': configuration.get('left_price', 0),
            'right_price': configuration.get('right_price', 0),
            'total_price': configuration.get('total_price', 0),
        }

        _logger.info(f"🧩 CPQ Config Received for {product_tmpl.display_name}:\n{json.dumps(config, indent=2)}")

        base_product = product_tmpl._ensure_configurator_product()
        if not base_product or not base_product.exists():
            raise UserError(_('No valid product could be determined.'))

        try:
            config_json = json.dumps(config, indent=2)
        except Exception as e:
            _logger.exception("❌ Failed to dump config_json")
            raise UserError("Invalid configuration data. Please check your selections.")

        ctx = env.context.copy() 
        ctx.update(kwargs.get("context", {})) 

        _logger.info(f"📦 Received context: {json.dumps(ctx, indent=2)}")

        active_model = ctx.get("active_model")
        active_id = ctx.get("active_id")
        active_sale_order_id = ctx.get("active_sale_order_id")
        sale_order = None
        existing_line = None
        if active_model == "sale.order.line" and active_id:
            existing_line = env['sale.order.line'].sudo().browse(active_id)
            if existing_line.exists():
                sale_order = existing_line.order_id
        elif active_model == "sale.order" and active_id:
            sale_order = env['sale.order'].sudo().browse(active_id)
        elif active_sale_order_id:
            sale_order = env['sale.order'].sudo().browse(active_sale_order_id)

        if not sale_order or not sale_order.exists():
            sale_order = env['sale.order'].sudo().search([('state', '=', 'draft')], limit=1)
            if not sale_order:
                raise UserError("No active draft Sale Order found. Please create a quotation first.")


        _logger.info(f"🧾 Using Sale Order: {sale_order.name} ({sale_order.id})")
        _logger.info(f"🔍 Processing: active_model={active_model}, active_id={active_id}, active_sale_order_id={active_sale_order_id}, existing_line={'Yes' if existing_line else 'No'}")

        summary_html = render_summary_html(env, sale_order, config)

        # line_vals = {
        #     'order_id': sale_order.id,
        #     'product_id': base_product.id,
        #     'name': config['name'],
        #     'cpq_configuration_json': config_json,
        #     'cpq_configuration_summary': summary_html,
        #     'product_uom': product_tmpl.uom_id.id,
        #     'product_uom_qty': config['quantity_to_make'],
        #     'price_unit': (
        #         config.get('total_price', 0) / config.get('quantity_to_make', 1)
        #         if config.get('quantity_to_make', 1)
        #         else 0
        #     ),
        # }

        product_taxes = base_product.taxes_id.filtered(lambda tax: tax.company_id == sale_order.company_id)
        taxes = product_taxes.ids

        line_vals = {
            'order_id': sale_order.id,
            'product_id': base_product.id,
            'name': config['name'],
            'cpq_configuration_json': config_json,
            'cpq_configuration_summary': summary_html,
            'product_uom': product_tmpl.uom_id.id,
            'product_uom_qty': config['quantity_to_make'],
            'price_unit': (
                config.get('total_price', 0) / config.get('quantity_to_make', 1)
                if config.get('quantity_to_make', 1)
                else 0
            ),
            # 'tax_id': [(6, 0, taxes)],  
            'tax_id': [(6, 0, taxes)] if taxes else False, # tax-exempt

        }


        def create_or_update_line(line):
            if line and line.exists():
                _logger.info(f"✏️ Updating existing sale.order.line {line.id}")
                line.write(line_vals)
                return line
            else:
                _logger.info(f"➕ Creating new sale.order.line")
                return env['sale.order.line'].sudo().create(line_vals)

        sale_order_line = create_or_update_line(existing_line)

        if sale_order.state != 'draft':
            sale_order_line.message_post(
                body=f"🛠️ CPQ configuration saved:<br/>{summary_html}",
                subtype_xmlid="mail.mt_note"
            )

        _logger.info(f"✅ Sale Order Line processed: {sale_order_line.id}")

        return {
            'product_id': base_product.id,
            'product_tmpl_id': product_tmpl.id,
            'sale_order_line_id': sale_order_line.id,
            'sale_order_id': sale_order.id,  
            'configuration': {
                'product_id': base_product.id,
                'name': config['name'],
                'cpq_configuration_json': config_json,
                'cpq_configuration_summary': summary_html,
                'quantity_to_make': config['quantity_to_make'],
                'laterality': config['laterality'],
                'split': config['split'],
                'selected': config['selected'],
            },
        }


# Helper extension for attribute lines
class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    def _cpq_get_combination_info_list(self):
        return [line._cpq_get_combination_info() for line in self]


 