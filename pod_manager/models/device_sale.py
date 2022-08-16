from odoo import models, fields


class CourseSale(models.Model):
    _inherit = 'product.template'
    _description = 'Products Add'

    name = fields.Char(string="Products")
    price = fields.Float(string="Price")
    image = fields.Binary(string='Photo', attachment=True)
