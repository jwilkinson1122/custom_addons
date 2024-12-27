from odoo import fields, models


class LateralityMatrix(models.Model):
    _name = "podiatry.laterality.matrix"
    _description = "Laterality Matrix for Sale Order"

    order_id = fields.Many2one(
        "sale.order",
        string="Sales Order",
        required=True,
    )
    laterality = fields.Selection(
        [
            ("left_only", "Left Only"),
            ("right_only", "Right Only"),
            ("bilateral", "Bilateral"),
        ],
        string="Foot Laterality",
        required=True,
    )
    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        required=True,
    )
    product_ids = fields.Many2many(
        "product.product",
        string="Products",
    )
