



from odoo import models, fields, api, _ 
from odoo.exceptions import UserError

class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_display_sale_btn = fields.Boolean(
        related="pos_config_id.pod_display_sale_btn", readonly=False)
    pos_select_order_state = fields.Selection(
        related="pos_config_id.select_order_state", readonly=False)

    @api.onchange('pos_pod_display_sale_btn')
    def _onchange_pod_display_sale_btn(self):
        stock_app = self.env['ir.module.module'].sudo().search([('name', '=', 'sale_management')], limit=1)
        print('\n\n\n stock_app',stock_app)
        if self.pos_pod_display_sale_btn:
            if stock_app.state != 'installed':
                self.pos_pod_display_sale_btn = False
                raise UserError('Sale Management Module not installed !\nPlease install Sale module first.')