from odoo import api, fields, models,_


class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sale_order_count = fields.Char()
