from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    active = fields.Boolean(default=True)
