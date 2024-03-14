from odoo import api, fields, models




class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"



    product_dimension = fields.Char(string="Dimensions")
    product_width = fields.Float(string="Width")
    product_height = fields.Float(string="Height")
    product_area = fields.Float(string="Area", compute='compute_area')
    quantity_appear = fields.Float(string="Qty", default=1)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', compute='compute_quantity')


    # index_num = fields.Integer(string="Index No")


    @api.onchange('product_height')
    def compute_area(self):
        for rec in self:
            if rec.product_width and rec.product_height:
                rec.product_area = (rec.product_width * rec.product_height) / 10000
                rec.product_qty = rec.product_area

            else:
                rec.product_area = 1
                rec.product_qty = rec.product_area


    @api.onchange('quantity_appear')
    def compute_quantity(self):
        for rec in self:
                rec.product_qty = rec.quantity_appear * rec.product_area

