from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    account_move = fields.Many2one(check_company=False)
