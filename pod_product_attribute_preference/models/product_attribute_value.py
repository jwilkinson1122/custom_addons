from odoo import models


class ProductAttributeValue(models.Model):
    _inherit = ["product.attribute.value", "product.attribute.preference.mixin"]
    _name = "product.attribute.value"
