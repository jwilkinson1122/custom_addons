from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    attribute_set_id = fields.Many2one(
        "product.attribute.set",
        string="Default Attribute Set",
    )