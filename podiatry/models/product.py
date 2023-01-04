# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Product(models.Model):
    _inherit = 'product.template'

    length = fields.Char(
        string='Length',
    )
    width = fields.Char(
        string='Width',
    )
    height = fields.Char(
        string='Height',
    )
    dimensions_uom_id = fields.Many2one(
        'uom.uom',
        'Dimension(UOM)',
        domain=lambda self: [
            ('category_id', '=', self.env.ref('uom.uom_categ_length').id)],
        help="Default Unit of Measure used for dimension."
    )

    weight_uom_id = fields.Many2one(
        'uom.uom',
        'Weight(UOM)',
        domain=lambda self: [
            ('category_id', '=', self.env.ref('uom.product_uom_categ_kgm').id)],
        help="Default Unit of Measure used for weight."
    )

    collection = fields.Char('Collection')

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id
                                  .currency_id.id,
                                  required=True)

    device_ok = fields.Boolean('Device')

    product_prices = fields.Monetary('Price', help="Price of the products")

    @api.onchange('device_ok')
    def onchange_product_type(self):
        self.type = 'consu'
        self.list_price = self.product_prices
