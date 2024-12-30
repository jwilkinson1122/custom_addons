from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quantity_booking = fields.Float(string='Quantity Booking', compute='_compute_quantity_booking')
    qty_after_booking = fields.Float(string='Quantity After Booking', compute='_compute_qty_after_booking')
    order_line_ids = fields.One2many('sale.order.line', 'product_template_id', string='Order Line')

    @api.depends('order_line_ids.qty_booking')
    def _compute_quantity_booking(self):
        for product in self:
            total_qty_booking = sum(line.qty_booking for line in product.order_line_ids if line.order_id.is_booking)
            product.quantity_booking = total_qty_booking

    @api.depends('quantity_booking', 'qty_available')
    def _compute_qty_after_booking(self):
        for template in self:
            template.qty_after_booking = template.qty_available - template.quantity_booking

    @api.depends('order_line_ids.qty_booking')
    def _compute_quantity_booking(self):
        for product in self:
            total_qty_booking = sum(line.qty_booking for line in product.order_line_ids if line.order_id.is_booking)
            product.quantity_booking = total_qty_booking


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_booking = fields.Float(related='product_tmpl_id.quantity_booking', string='Quantity Booking', readonly=True)
    qty_after_booking = fields.Float(related='product_tmpl_id.qty_after_booking', string='Quantity After Booking',
                                     readonly=True)


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    purchase_date = fields.Date(string="Purchase Date")
