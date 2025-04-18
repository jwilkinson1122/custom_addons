from odoo import api, fields, models, _
import json
from datetime import datetime
from odoo.addons.cpq.helpers.summary_helper import get_cpq_config_dict

class CreateProductWizard(models.TransientModel):
    _name = "create.product.wizard"
    _description = "Confirm Product Creation from CPQ Configuration"

    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line", required=True, readonly=True)
    configuration_summary = fields.Html(string="Configuration Summary", readonly=True)
    preview_name = fields.Char(string="Product Name", readonly=True)
    preview_internal_ref = fields.Char(string="Internal Reference", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        line_id = self.env.context.get('default_sale_order_line_id')
        if not line_id:
            return res

        line = self.env['sale.order.line'].browse(line_id).exists()
        if not line or not line.cpq_configuration_json:
            return res

        config = get_cpq_config_dict(line)
        if not config:
            return res  # or raise ValidationError("Invalid CPQ configuration data.")

        today_str = datetime.today().strftime("%Y%m%d")
        customer_initials = ''.join(
            word[0].upper() for word in (line.order_id.partner_id.name or "").split() if word
        )
        internal_ref = f"CFG-{today_str}-{line.id}-{customer_initials or 'CUST'}"
        name = config.get('name') or f"{line.product_template_id.name} Custom"

        res.update({
            'preview_internal_ref': internal_ref,
            'preview_name': name,
        })

        return res

    def action_confirm_create(self):
        self.ensure_one()
        return self.sale_order_line_id.action_create_product_from_configuration()

    def action_print_summary(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.report',
            'report_name': 'cpq_sale.report_cpq_configuration_summary',
            'report_type': 'qweb-pdf',
            'context': {
                'active_ids': [self.sale_order_line_id.id],
                'active_model': 'sale.order.line',
            },
        }
