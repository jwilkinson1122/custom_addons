from odoo import models


class ProductAttribute(models.Model):
    _inherit = ["product.attribute", "product.attribute.preference.mixin"]
    _name = "product.attribute"
