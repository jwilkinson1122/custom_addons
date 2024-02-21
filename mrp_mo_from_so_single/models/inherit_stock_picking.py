from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.picking"

    product_width = fields.Float(string="Width")
    product_length = fields.Float(string="Height")
    product_area = fields.Float(string="Area")
