import logging
from datetime import datetime
from datetime import date, timedelta
from odoo.fields import Field
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cpq.helpers.summary_helper import render_summary_html

import json

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # def action_config_start(self):
    #     self.ensure_one()

    #     cpq_products = self.env["product.template"].search([("cpq_ok", "=", True)])
    #     if not cpq_products:
    #         raise UserError("No CPQ-enabled products found.")

    #     if len(cpq_products) == 1:
    #         return cpq_products.action_configure_cpq()

    #     return {
    #         "type": "ir.actions.act_window",
    #         "name": "Select CPQ Product",
    #         "res_model": "product.template",
    #         "view_mode": "tree",
    #         "target": "current",
    #         "domain": [("cpq_ok", "=", True)],
    #         "context": {
    #             "active_model": "sale.order",  
    #             "active_id": self.id,          
    #             "default_cpq_ok": True,
    #         },
    #     }

class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "mail.thread"]
    _name = "sale.order.line"

    product_template_id_cpq_ok = fields.Boolean(related="product_template_id.cpq_ok")

    # order_line_image = fields.Binary(string="Image",
    #                                  related="product_id.image_128",
    #                                  help="This field represents the image "
    #                                       "associated with the product on the "
    #                                       "sale order line."
    #                                  )


    cpq_configuration_json = fields.Json(
        string="CPQ Configuration",
        help="Stores selected laterality and option data for CPQ products."
    )

    cpq_laterality = fields.Selection(
        selection=[
            ('left', 'Left Only'),
            ('right', 'Right Only'),
            ('bilateral', 'Bilateral'),
        ],
        string="Laterality",
        compute='_compute_cpq_laterality',
        store=True
    )

    cpq_quantity_to_make = fields.Integer(
        string="Pairs to Make",
        compute="_compute_cpq_quantity_to_make",
        store=True
    )

    cpq_configuration_summary = fields.Html(
        string="CPQ Summary",
        compute="_compute_cpq_configuration_summary",
        store=True,
    )

    cpq_product_created = fields.Boolean(
        string="CPQ Product Created",
        compute="_compute_cpq_product_created",
        store=True
    )

    def toggle_debug_cpq_json(self):
        # Placeholder logic: in real use, you'd probably use context or a transient field to show/hide.
        raise UserError("This would show/hide CPQ JSON — placeholder.")
    
    @api.onchange('cpq_configuration_json')
    def _onchange_cpq_configuration(self):
        for line in self:
            if not line.cpq_configuration_json:
                continue

            try:
                config = json.loads(line.cpq_configuration_json)
                _logger.info("🧩 [CPQ] Applying configuration to order line: %s", json.dumps(config, indent=2))

                line.name = config.get("name") or line.name
                line.product_uom_qty = config.get("quantity_to_make", line.product_uom_qty)

                # Optional: add to chatter only after save
                summary_html = render_summary_html(self.env, line.order_id, config, mode="chatter")
                _logger.info("🖨️ [CPQ] Generated Summary HTML:\n%s", summary_html)

                line.message_post(
                    body=f"""
                        <b>🛠️ CPQ Configuration Applied:</b><br/>
                        {summary_html}
                    """,
                    subtype_xmlid="mail.mt_note",
                )

            except Exception as e:
                _logger.warning(f"⚠️ Failed to parse CPQ config JSON: {e}")

    @api.depends('cpq_configuration_json')
    def _compute_cpq_laterality(self):
        for line in self:
            config = line.cpq_configuration_json or {}
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except Exception:
                    config = {}
            line.cpq_laterality = config.get('laterality')

    @api.depends("cpq_configuration_json")
    def _compute_cpq_quantity_to_make(self):
        for line in self:
            config = line.cpq_configuration_json or {}
            if isinstance(config, str):
                try:
                    config = json.loads(config)
                except Exception:
                    config = {}
            line.cpq_quantity_to_make = config.get("quantity_to_make", 1)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and self.product_id.cpq_ok:
            tmpl = self.product_id.product_tmpl_id

            return {
                "type": "ir.actions.client",
                "tag": "cpq.ConfigureDialogAction",
                "context": {
                    "active_model": "sale.order.line",
                    "active_id": self.id,
                    "cpq_product_template_id": tmpl.id,
                    "cpq_initial_config": self.cpq_configuration_json,
                    "from_sale_order": True,
                    "redirect_to_line": True,
                    "orderId": self.order_id.id,
                    "currencyId": self.order_id.currency_id.id,
                    "soDate": str(self.order_id.date_order),
                    "companyId": self.order_id.company_id.id,
                },
            }
        
    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super()._onchange_product_id_warning()
        if self.product_id.cpq_ok and self.product_id.cpq_description_sale_tmpl:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)

            name = product.product_tmpl_id._cpq_render_inline_template(
                product.cpq_description_sale_tmpl,
                extras={
                    "record": product,
                    "tmpl": self,
                },
            )

            if name:
                self.name = name
        return res

    @api.depends("cpq_configuration_json")
    def _compute_cpq_name_suffix(self):
        for line in self:
            config = self._parse_json_field(line.cpq_configuration_json)
            if not config:
                line.name = line.product_id.display_name or line.product_id.name
                continue

            selections = config.get("selected", {})
            side = config.get("laterality", "").capitalize()
            summary = ", ".join(str(v) for v in selections.values()) if isinstance(selections, dict) else ""

            if side and summary:
                line.name = f"{line.product_id.name} - {side} ({summary})"
            elif side:
                line.name = f"{line.product_id.name} - {side}"
            else:
                line.name = line.product_id.name

    @api.onchange('cpq_configuration_json')
    def _onchange_cpq_pricing(self):
        config = self.cpq_configuration_json or {}
        if isinstance(config, str):
            try:
                config = json.loads(config)
            except Exception:
                config = {}

        qty = config.get("quantity_to_make", 1)
        total_extra = 0

        selected = config.get("selected", {})
        if isinstance(selected, dict):
            ptav_ids = [int(k) for k in selected if k.isdigit()]
            ptavs = self.env["product.template.attribute.value"].browse(ptav_ids)
            total_extra = sum(ptav.price_extra for ptav in ptavs)

        base_price = self.product_template_id.list_price
        if config.get("laterality") == "bilateral":
            base_price *= 2

        final_price = (base_price + total_extra) * qty
        _logger.info("💸 [CPQ] Pricing computed: Base: %.2f, Extras: %.2f, Qty: %d, Final: %.2f",
                    base_price, total_extra, qty, final_price)

        self.price_unit = final_price

    @api.depends('cpq_configuration_json')
    def _compute_cpq_configuration_summary(self):
        for line in self:
            config = line.cpq_configuration_json
            if not config:
                line.cpq_configuration_summary = "No configuration available."
                continue

            try:
                if isinstance(config, str):
                    config = json.loads(config)

                _logger.info(f"🧩 Generating summary for Sale Order Line {line.id}")
                _logger.info(f"Config Data: {config}")

                summary_html = render_summary_html(self.env, line.order_id, config)
                line.cpq_configuration_summary = summary_html

            except Exception as e:
                _logger.warning(f"⚠️ Failed to generate summary HTML: {e}")
                line.cpq_configuration_summary = "⚠️ Error generating summary."

    def edit_cpq_configuration(self):
        self.ensure_one()
        tmpl = self.product_id.product_tmpl_id

        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order.line",
                "active_id": self.id,
                "cpq_product_template_id": tmpl.id,
                "cpq_initial_config": self.cpq_configuration_json,
                "from_sale_order": True,
                "redirect_to_line": True,
                "orderId": self.order_id.id,
                "currencyId": self.order_id.currency_id.id,
                "soDate": str(self.order_id.date_order),
                "companyId": self.order_id.company_id.id,
            },
        }

    def _compute_cpq_product_created(self):
        for line in self:
            line.cpq_product_created = bool(
                line.product_id and line.product_id.default_code and line.product_id.default_code.startswith("CFG-")
            )

    def action_open_create_product_wizard(self):
        self.ensure_one()

        if not self.cpq_configuration_json:
            raise UserError("No CPQ configuration found on this line.")

        return {
            'name': _("Confirm Product Creation"),
            'type': 'ir.actions.act_window',
            'res_model': 'create.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_line_id': self.id,
                'default_configuration_summary': self.cpq_configuration_summary,
            },
        }

    def action_create_product_from_configuration(self):
        self.ensure_one()

        if not self.cpq_configuration_json:
            raise UserError("No CPQ configuration found on this line.")

        try:
            config = json.loads(self.cpq_configuration_json)
        except Exception as e:
            raise UserError(f"Invalid CPQ configuration JSON: {e}")

        # ✅ Safety check
        if self.product_id and self.product_id.default_code and self.product_id.default_code.startswith("CFG-"):
            raise UserError("This line is already linked to a custom CPQ product.")

        product_tmpl = self.product_template_id
        if not product_tmpl:
            raise UserError("No product template linked to this order line.")

        today_str = datetime.today().strftime("%Y%m%d")
        customer_initials = ''.join(word[0].upper() for word in (self.order_id.partner_id.name or "").split() if word)
        internal_ref = f"CFG-{today_str}-{self.id}-{customer_initials or 'CUST'}"

        product_name = config.get('name') or f"{product_tmpl.name} Custom"

        total_extra = self._calculate_total_extras(config)

        description_sale = self._generate_cpq_description(config, total_extra)
        description_purchase = description_sale

        image = product_tmpl.image_1920

        new_product = self.env['product.product'].create({
            'product_tmpl_id': product_tmpl.id,
            'default_code': internal_ref,
            'name': product_name,
            'lst_price': total_extra or self.price_unit,
            'description_sale': description_sale,
            'description_purchase': description_purchase,
            'image_1920': image,
        })

        _logger.info(f"🆕 Created product {new_product.display_name} ({new_product.id}) from CPQ config.")

        self._apply_cpq_attributes_to_product(config, new_product)

        self.message_post(body=_(
            f"🧩 Product <b>{new_product.display_name}</b> created from CPQ configuration."
        ))
        new_product.message_post(body=_(
            f"🧩 Created from CPQ configuration on Sale Order <b>{self.order_id.name}</b>."
        ))

        self.product_id = new_product.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'res_id': new_product.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _generate_cpq_description(self, config, total_extra):
        parts = [
            f"🦶 Laterality: {config.get('laterality', '').capitalize()}",
            f"📦 Quantity: {config.get('quantity_to_make', 1)}",
        ]

        selected = config.get("selected", {})
        if selected:
            parts.append("🧩 Selected Options:")
            for _, value in selected.items():
                parts.append(f"• {value}")

        if total_extra:
            parts.append(f"💰 Total Extras: {total_extra:.2f}")

        total_price = config.get('total_price')
        if total_price:
            parts.append(f"📊 Total Price: {total_price:.2f}")

        return "\n".join(parts)

    def _calculate_total_extras(self, config):
        selected = config.get('selected', {})
        if not selected:
            return 0

        ptav_ids = [int(k) for k in selected if k.isdigit()]
        ptavs = self.env['product.template.attribute.value'].browse(ptav_ids)

        total_extra = sum(ptav.price_extra for ptav in ptavs)
        _logger.info(f"🧩 Total extras calculated: {total_extra}")
        return total_extra

    def _apply_cpq_attributes_to_product(self, config, product):
        selected = config.get('selected', {})
        if not selected:
            return

        ptav_ids = [int(k) for k in selected if k.isdigit()]
        ptav_records = self.env['product.template.attribute.value'].browse(ptav_ids)

        if not ptav_records:
            return

        product.write({
            'product_template_attribute_value_ids': [(6, 0, ptav_records.ids)],
        })

        _logger.info(f"🧩 Applied CPQ attributes to product {product.display_name}: {ptav_records.mapped('name')}")
