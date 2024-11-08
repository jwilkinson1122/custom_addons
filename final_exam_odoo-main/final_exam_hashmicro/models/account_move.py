from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', store=True)

