from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = 'complete.pair.order'

    sal = fields.Many2one(
        'sale.order', default=lambda self: self.env.context.get('active_id'))
    customer_id = fields.Many2one(related='sal.partner_id')
    prescription = fields.Many2one(
        'doctor.prescription', string='Prescription(Rx)', required=True)
    frame = fields.Many2one('product.product', string='Frames',
                            domain="[('categ_id', '=', 'Frames')]", required=True)
    lens = fields.Many2one('product.product', string='Lens',
                           domain="[('categ_id', '=', 'Lens')]", required=True)

    # sale_order_id = fields.Many2one('sale.order')
    def show_btn(self):
        SaleOrderLine = self.env['sale.order.line'].with_context(
            tracking_disable=True)
        SaleOrderLine.create({
            'name': 'Complete Pair Order',
            'display_type': 'line_section',
            'order_id': self.env.context.get('active_id'),
        })
        SaleOrderLine = self.env['sale.order.line'].create({
            'name': self.frame.name,
            'product_id': self.frame.id,
            'product_uom_qty': 1,
            'qty_delivered': 1,
            'product_uom': self.frame.uom_id.id,
            'price_unit': self.frame.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        SaleOrderLine.product_id_change()

        sale_order_line2 = self.env['sale.order.line'].create({
            'name': self.lens.name,
            'product_id': self.lens.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.lens.uom_id.id,
            'price_unit': self.lens.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line2.product_id_change()
