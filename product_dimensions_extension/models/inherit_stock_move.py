from odoo import models, fields, api, _


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

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

    @api.onchange('qty_to_do')
    def compute_qty_done(self):
        for rec in self:
            rec.qty_done = rec.product_area


class StockMoveInheritance(models.Model):
    _inherit = "stock.move"

    product_width = fields.Float(string="Width")
    product_height = fields.Float(string="Height")
    product_area = fields.Float(string="Area")
    qty_to_do = fields.Float('Done')
