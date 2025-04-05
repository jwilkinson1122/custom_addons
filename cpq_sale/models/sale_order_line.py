import logging
from datetime import date, timedelta
from odoo.fields import Field
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cpq.helpers.summary_helper import render_summary_html

import json

_logger = logging.getLogger(__name__)


# class SaleOrder(models.Model):
#     _inherit = "sale.order"

#     def action_config_start(self):
#         """Return action to start configuration wizard"""
#         configurator_obj = self.env["product.configurator.sale.order"]
#         ctx = dict(
#             self.env.context,
#             default_order_id=self.id,
#             wizard_model="product.configurator.sale.order",
#             allow_preset_selection=True,
#         )
#         return configurator_obj.with_context(**ctx).get_wizard_action()


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "mail.thread"]
    _name = "sale.order.line"

    product_template_id_cpq_ok = fields.Boolean(related="product_template_id.cpq_ok")
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
                line.name = config.get("name") or line.name
                line.product_uom_qty = config.get("quantity_to_make", line.product_uom_qty)

                # Optional: add to chatter only after save
                line.message_post(
                    body=f"🛠️ CPQ configuration applied:<br/>{config.get('cpq_configuration_summary', '')}",
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
        self.price_unit = (base_price + total_extra) * qty

    @api.depends('cpq_configuration_json')
    def _compute_cpq_configuration_summary(self):
        for line in self:
            if line.cpq_configuration_json:
                config = json.loads(line.cpq_configuration_json)
                line.cpq_configuration_summary = render_summary_html(self.env, line.order_id, config)



    # @api.depends('cpq_configuration_json')
    # def _compute_cpq_configuration_summary(self):
    #     for line in self:
    #         config = line.cpq_configuration_json or {}
    #         if isinstance(config, str):
    #             try:
    #                 config = json.loads(config)
    #             except Exception:
    #                 config = {}

    #         side = config.get("laterality", "N/A").capitalize()
    #         selected = config.get("selected", {})
    #         if isinstance(selected, dict):
    #             summary = ", ".join(str(v) for v in selected.values())
    #             line.cpq_configuration_summary = f"{side} - {summary}" if summary else side
    #         else:
    #             line.cpq_configuration_summary = side
                


    def edit_cpq_configuration(self):
        self.ensure_one()
        tmpl = self.product_id.product_tmpl_id

        return {
            "type": "ir.actions.client",
            "tag": "cpq.ConfigureDialogAction",
            "context": {
                "active_model": "sale.order.line",
                "active_id": self.id,
                "from_sale_order": True,
                "redirect_to_line": True,
                "cpq_initial_config": self.cpq_configuration_json,  # 👈 preload config
            },
        }
