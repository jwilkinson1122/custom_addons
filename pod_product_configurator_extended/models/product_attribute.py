from odoo import models, api, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    do_display_image = fields.Boolean()

    display_type = fields.Selection(selection_add=[
        ('dimension', 'Dimension'),
    ], ondelete={'dimension': 'cascade'})
