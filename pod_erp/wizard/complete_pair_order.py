from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = 'complete.pair.order'

    sal = fields.Many2one(
        'sale.order', default=lambda self: self.env.context.get('active_id'))
    customer_id = fields.Many2one(related='sal.partner_id')
    prescription = fields.Many2one(
        'podiatry.prescription', string='Prescription(Rx)', required=True)
    shell = fields.Many2one('product.product', string='Shells',
                            domain="[('categ_id', '=', 'Shells')]", required=True)
    topcover = fields.Many2one('product.product', string='Topcover',
                               domain="[('categ_id', '=', 'Topcover')]", required=True)

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
            'name': self.shell.name,
            'product_id': self.shell.id,
            'product_uom_qty': 1,
            'qty_delivered': 1,
            'product_uom': self.shell.uom_id.id,
            'price_unit': self.shell.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        SaleOrderLine.product_id_change()

        sale_order_line2 = self.env['sale.order.line'].create({
            'name': self.topcover.name,
            'product_id': self.topcover.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.topcover.uom_id.id,
            'price_unit': self.topcover.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line2.product_id_change()
