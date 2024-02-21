from odoo import fields, models


class PresaleLineModel(models.Model):
    _name = "presale.order.line"
    _description = "Presale order line"

    presale_order_id = fields.Many2one("presale.order", required=True)
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity")
    price = fields.Float(string="Price")
