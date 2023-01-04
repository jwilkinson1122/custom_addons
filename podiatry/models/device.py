from odoo import models, fields, api


class ProductDevice(models.Model):
    _inherit = 'product.template'
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
