from odoo import fields, models


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    is_preference = fields.Boolean(
        related="attribute_id.is_preference",
    )
