from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quantity_booking = fields.Float(string='Quantity Booking')
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

    # @api.constrains('quantity_booking')
    # def _check_max_booking_order(self):
    #     for product in self:
    #         config = self.env['booking.order.config'].search([], limit=1)
    #         if config and product.quantity_booking > config.max_booking_order:
    #             raise ValidationError(
    #                 _(f'Quantity booking cannot exceed the maximum booking order of %s') % config.max_booking_order)

