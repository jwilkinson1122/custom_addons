from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.picking"

    product_width = fields.Float(string="Width")
    product_height = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    qty_to_do = fields.Float('Done', default=0.0, compute='compute_area')

    @api.onchange('product_height')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_height:
                rec.product_area = (rec.product_width * rec.product_height) / 10000
                rec.qty_to_do = rec.product_area
            else:
                rec.product_area = 1
                rec.qty_to_do = 1
