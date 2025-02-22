

from odoo import models, fields, api

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    last_sold_price = fields.Monetary(string="Last Sold Price", compute="_compute_last_sold_price", store=False, default=0.000, currency_field='currency_id')
    last_sold_discount = fields.Float(string="Last Sold Discount", store=False, default=0)
    last_invoice_date = fields.Char(string="Last Sold Date", store=False)
    last_invoice_num = fields.Char(string="Last Invoice Number", store=False)
    currency_symbol = fields.Char(string="Currency Symbol", store=False)

    @api.depends('product_id')
    def _compute_last_sold_price(self):
        for line in self:
            print("line.product_id: ", line.product_id)
            print("line.order_id.partner_id: ", line.order_id.partner_id)
            if line.product_id and line.order_id.partner_id is not None:
                
                # last_sale = self.env['sale.order.line'].search([
                #     ('product_id', '=', line.product_id.id),
                #     ('order_id.partner_id', '=', line.order_id.partner_id.id),
                #     ('order_id.state', 'in', ['sale', 'done'])
                # ], order='create_date desc', limit=1)
                
                last_inv_line = self.env['account.move.line'].search([
                    ('product_id', '=', line.product_id.id),
                    ('move_id.partner_id', '=', line.order_id.partner_id.id),
                    ('move_id.state', 'in', ['posted'])
                ], order='invoice_date desc', limit=1)
                
                if last_inv_line is not None and last_inv_line.price_subtotal not in [None, 0]:
                    # print('Price Updated = ', last_inv_line.price_subtotal)
                    # print('Invoice_date = ', last_inv_line.move_id.invoice_date)

                    line.last_sold_price = last_inv_line.price_subtotal
                    line.last_sold_discount = last_inv_line.discount
                    line.last_invoice_date  = last_inv_line.move_id.invoice_date.strftime('%Y/%m/%d')
                    line.last_invoice_num  = last_inv_line.move_id.name
                    line.currency_symbol = line.currency_id.symbol
                else:
                    line.last_sold_price = 0


    def view_last_sold(self):
        print('view_last_sold ::::::::::::::::::::::::::::: ')

        pass
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'view_last_sold',  # Custom action tag
        #     'params': {
        #         'message': 'Button clicked via Python backend!',
        #     },
        # }