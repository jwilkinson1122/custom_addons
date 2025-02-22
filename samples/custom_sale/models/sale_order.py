from math import floor

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    def apply_round_off(self):
        
        for order in self:
            product = self.env['product.product'].search([('name', '=', 'Round Off')], limit=1)
            if product:
                round_off_amount = (floor(order.amount_total * 10) / 10)
                round_off = round(order.amount_total - round_off_amount, 3)
                if(round_off > 0):
                    self.env['sale.order.line'].create({
                        'order_id': self.id,  # This links the new line to the current sale order
                        'product_id': product.id,  # Set the product to be added
                        'product_uom_qty': 1,  # Quantity (set as per your requirement)
                        'price_unit': -round_off,  # Price (you can define a custom price if needed)
                        'name': product.name,  # Product name will appear in the order line
                        'tax_id': False
                    })
        
            
            
