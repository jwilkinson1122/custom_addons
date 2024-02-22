from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    description = fields.Html(translate=True)
