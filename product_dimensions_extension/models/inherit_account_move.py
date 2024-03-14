from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    product_area = fields.Float(string="Area")
    product_dimension = fields.Char(string="Dimensions")
    product_width = fields.Float(string="Width")
    product_height = fields.Float(string="Height")
