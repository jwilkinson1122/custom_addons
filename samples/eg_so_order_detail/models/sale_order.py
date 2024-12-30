from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    product_text = fields.Char(string="product Name", compute='_compute_sale_detail')
    product_qty = fields.Float(string="Quantity", compute='_compute_sale_detail')
    order_detail = fields.Text(string="Order Detail", compute='_compute_sale_detail')

    @api.depends('order_line.product_id', 'order_line.product_uom_qty')
    def _compute_sale_detail(self):
        product_name = ''
        for record in self:
            for line in record.order_line:
                product_name += line.product_id.name + ": " + str(line.product_uom_qty) + "\n"
                record.order_detail = product_name
