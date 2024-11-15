from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    attached_product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_attached_rel",
        string="Attached Products",
        help="Similar to optional products, although they're added automatically to the"
        "sale order and optionally removed when the main product goes away.",
    )
