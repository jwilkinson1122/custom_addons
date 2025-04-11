from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.http import Controller, request, route
from ..helpers.summary_helper import render_summary_html
import logging
import json

_logger = logging.getLogger(__name__)


class ProductConfiguratorController(Controller):

    def _log_context(self, env, label="Context"):
        try:
            formatted_context = json.dumps(env.context, indent=2, default=str)
            _logger.info(f"🧩 {label}:\n{formatted_context}")
        except Exception as e:
            _logger.warning(f"⚠️ Failed to format context: {e}")

    def _cpq_extract_from_combination(self, product_tmpl_id, combination):
        ptav_ids = request.env["product.template.attribute.value"]
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

        product_tmpl = env["product.template"].browse(product_tmpl_id).sudo()
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
                price_extra = (
                    pricelist._get_product_price_extra(ptav, currency=currency, company=env.company)
                    if pricelist else ptav.currency_id._convert(
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

                side_prices = {"left": price_extra, "right": price_extra}

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
        env = request.env
        product_tmpl = env["product.template"].browse(product_tmpl_id).sudo()

        if not product_tmpl.cpq_ok:
            return {"valid": False, "errors": {"general": _("Not CPQ Enabled!")} }

        ptav_ids, custom_dict = self._cpq_extract_from_combination(product_tmpl, combination)
        variant_ok, msg = product_tmpl._cpq_ensure_valid_values(
            ptav_ids, custom_dict, raise_on_invalidity=False, validate_only=True
        )

        return {"valid": variant_ok, "errors": msg}


    @route('/cpq/<int:product_tmpl_id>/configure', type='json', auth='user')
    def cpq_configure(self, product_tmpl_id, configuration):
        _logger.info(f"🧩 Request params: {request.params}")
        _logger.info(f"🧩 Request context: {env.context}")
        _logger.info(f"🧩 JsonRequest data: {getattr(request, 'jsonrequest', None)}")

        env = request.env
        self._log_context(env, label="Merged Context")

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
        except Exception:
            _logger.exception("❌ Failed to dump config_json")
            raise UserError("Invalid configuration data. Please check your selections.")

        ctx = env.context
        active_model = ctx.get("active_model")
        # ✅ Convert safely to int
        active_id = int(ctx.get("active_id") or 0)
        active_sale_order_id = int(ctx.get("active_sale_order_id") or 0)

        _logger.info(f"🔍 Context check: active_model={active_model}, active_id={active_id} ({type(active_id)}), active_sale_order_id={active_sale_order_id} ({type(active_sale_order_id)})")

        # 🧩 Safe fallback order lookup
        sale_order = None
        sale_order_line = env['sale.order.line'].sudo().browse(active_id) if active_model == 'sale.order.line' and active_id else env['sale.order.line']
        if sale_order_line and sale_order_line.exists():
            sale_order = sale_order_line.order_id

        # ✅ Prefer active_sale_order_id if sale_order is not found
        if not sale_order and active_sale_order_id:
            sale_order_candidate = env['sale.order'].sudo().browse(active_sale_order_id)
            if sale_order_candidate.exists():
                sale_order = sale_order_candidate
            else:
                _logger.warning(f"⚠️ active_sale_order_id {active_sale_order_id} is invalid.")

        if not sale_order or not sale_order.exists():
            _logger.error(f"🚨 No Sale Order found! active_id={active_id}, active_sale_order_id={active_sale_order_id}")
            raise UserError("No active Sale Order found. Please launch from an order line or create a quotation.")

        _logger.info(f"🧾 Using Sale Order: {sale_order.name} ({sale_order.id})")

        summary_html = render_summary_html(env, sale_order, config)

        line_vals = self._prepare_cpq_line_vals(env, sale_order, base_product, product_tmpl, config, summary_html, config_json)

        _logger.info(f"🧩 CPQ: Prepared line_vals:\n{json.dumps(line_vals, indent=2, default=str)}")

        def create_or_update_line(line):
            if line and line.exists():
                _logger.info(f"✏️ Updating existing sale.order.line {line.id}")
                line.write(line_vals)
                return line
            else:
                _logger.info(f"➕ Creating new sale.order.line")
                return env['sale.order.line'].sudo().create(line_vals)

        sale_order_line = create_or_update_line(sale_order_line)

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


        def _prepare_cpq_line_vals(self, env, sale_order, base_product, product_tmpl, config, summary_html, config_json):
            taxes = (base_product.taxes_id or sale_order.fiscal_position_id.map_tax(base_product.taxes_id)).filtered(lambda t: t.company_id == sale_order.company_id)

            return {
                'order_id': sale_order.id,
                'product_id': base_product.id,
                'name': config['name'],
                'cpq_configuration_json': config_json,
                'cpq_configuration_summary': summary_html,
                'product_uom': product_tmpl.uom_id.id,
                'product_uom_qty': config['quantity_to_make'],
                'price_unit': (
                    round(config.get('total_price', 0) / config.get('quantity_to_make', 1), 2)
                    if config.get('quantity_to_make', 1)
                    else 0
                ),
                'tax_id': [(6, 0, taxes.ids)],
            }
