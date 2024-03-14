from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Products that are attached to a partner, and thus, can be purchased
    restricted_product_ids = fields.Many2many('product.product', string="Product Preferences")
    product_partner = fields.Boolean()
