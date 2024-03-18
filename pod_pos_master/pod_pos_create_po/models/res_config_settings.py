


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResConfigInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_dispaly_purchase_btn = fields.Boolean(
        related="pos_config_id.pod_dispaly_purchase_btn", readonly=False)
    pos_select_purchase_state = fields.Selection(
        related="pos_config_id.select_purchase_state", readonly=False)

    @api.onchange('pos_pod_dispaly_purchase_btn')
    def _onchange_pod_display_purchase_btn(self):
        stock_app = self.env['ir.module.module'].sudo().search([('name', '=', 'purchase')], limit=1)
        if self.pos_pod_dispaly_purchase_btn:
            if stock_app.state != 'installed':
                self.pos_pod_dispaly_purchase_btn = False
                raise UserError('Purchase Module not installed ! \n Please install Sale module first.')