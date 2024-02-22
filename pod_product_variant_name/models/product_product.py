from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    name = fields.Char(index="trigram", required=True, translate=True)
