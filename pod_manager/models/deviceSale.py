from odoo import models, fields


class CourseSale(models.Model):
    _inherit = 'product.template'
    _description = 'Medical Device Add'

    name = fields.Char(string="Medical Device")
    price = fields.Float(string="Price")
    image = fields.Binary(string='Photo', attachment=True)
