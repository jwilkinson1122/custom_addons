from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_tax_state = fields.Selection(related="order_id.price_tax_state")
