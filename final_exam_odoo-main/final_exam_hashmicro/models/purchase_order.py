from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_booking = fields.Boolean(string='Is Booking', default=False)
    booking_order_id = fields.Many2one('sale.order', string='Booking Order')
    invoice_ids = fields.One2many('account.move', 'purchase_id', string='Invoices')

    # (optional) fitur refresh price
    def action_refresh_price(self):
        for line in self.order_line:
            supplierinfo = line.product_id.seller_ids.filtered(
                lambda r: r.product_code == line.product_id.default_code and
                          r.partner_id.name == line.order_id.partner_id.name
            )
            if supplierinfo:
                line.price_unit = supplierinfo[0].price

    # smart Button
    def action_view_booking_orders(self):
        if self.is_booking:
            action = self.env.ref('sale.action_quotations').read()[0]
            action['domain'] = [('id', '=', self.booking_order_id.id)]
            return action
        else:
            return {
                'warning': {
                    'title': 'Not a Booking Order',
                    'message': 'This record is not a booking order.',
                }
            }

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        self.update_vendor_price()
        self.update_button_confirm()
        self.create_invoice_order()
        self.update_purchase_date()

        return res

    def update_button_confirm(self):
        for order in self:
            if order.state == 'purchase':
                order.name = self.env["ir.sequence"].next_by_code('purchase.order.seq') or _("New")
        return super(PurchaseOrder, self).button_confirm()

    def update_vendor_price(self):
        for line in self.order_line:
            products = self.env['product.product'].browse(line.product_id.id)
            for vendor in products.seller_ids:
                if self.partner_id.id == vendor.name.id:
                    vendor.write({
                        'price': line.price_unit
                    })

    def create_invoice_order(self):
        for order in self:
            if order.state == 'purchase':
                # Create invoice for purchase order
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': order.partner_id.id,
                    'invoice_origin': order.name,
                    'invoice_date': fields.Date.context_today(self),
                    'purchase_id': order.id,
                    'invoice_line_ids': [],
                }
                for line in order.order_line:
                    # Ensure account_id is set correctly
                    account_id = line.product_id.categ_id.property_account_expense_categ_id.id
                    if not account_id:
                        raise ValidationError(f"Product {line.product_id.name} does not have an expense account set.")
                    invoice_line_vals = {
                        'name': line.name,
                        'quantity': line.product_qty,
                        'price_unit': line.price_unit,
                        'product_id': line.product_id.id,
                        'account_id': account_id,
                    }
                    invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

                invoice = self.env['account.move'].create(invoice_vals)
                invoice.action_post()  # Validate the invoice
                order.invoice_ids = [(4, invoice.id)]

    def update_purchase_date(self):
        for line in self.order_line:
            products = self.env['product.product'].browse(line.product_id.id)
            purchase_date = date.today()
            for vendor in products.seller_ids:
                if self.partner_id.id == vendor.name.id:
                    vendor.write({
                        'purchase_date': purchase_date
                    })
