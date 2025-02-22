
from math import floor

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = 'account.move'

    def apply_round_off(self):
        print('apply_round_off:::::::::::::::::')
        for order in self:
            product = self.env['product.product'].search([('name', '=', 'Round Off')], limit=1)
            if product:
                round_off_amount = (floor(order.amount_total * 10) / 10)
                round_off = round(order.amount_total - round_off_amount, 3)
                if(round_off > 0):
                    account = self.env['account.account'].search([('name', '=', 'Round Off')], limit=1)

                    self.env['account.move.line'].create({
                        'move_id': self.id,  # Link the line to the current invoice
                        'product_id': product.id,  # Product to be added
                        'quantity': 1,  # Quantity of the product (you can change this as needed)
                        'price_unit': -round_off,  # Price of the product (using the standard price)
                        'name': product.name,  # Description that will appear in the invoice line
                        'account_id': account.id,  # Default income account (or specify an account manually)
                        'tax_ids': False,  # Taxes linked to the product
                    })


    

