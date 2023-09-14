

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    sale_order_id = fields.Many2one("sale.order")
