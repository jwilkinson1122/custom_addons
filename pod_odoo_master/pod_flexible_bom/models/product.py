from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    flexible_bom = fields.Boolean(string="Flexible BOM")
    margin = fields.Float(string="Margin")
