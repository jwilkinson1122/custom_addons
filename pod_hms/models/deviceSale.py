from odoo import models, fields


class DeviceSale(models.Model):
    _inherit = 'product.template'
    _description = 'Products Add'

    name = fields.Char(string="Products")
    price = fields.Float(string="Price")
    image = fields.Binary(string='Photo', attachment=True)
