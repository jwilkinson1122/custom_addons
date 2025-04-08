from odoo import api, fields, models, _
import json
from datetime import datetime

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

        line = self.env['sale.order.line'].browse(self.env.context.get('default_sale_order_line_id'))
        config_json = line.cpq_configuration_json

        if config_json:
            config = json.loads(config_json)

            today_str = datetime.today().strftime("%Y%m%d")
            customer_initials = ''.join(word[0].upper() for word in (line.order_id.partner_id.name or "").split() if word)
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
