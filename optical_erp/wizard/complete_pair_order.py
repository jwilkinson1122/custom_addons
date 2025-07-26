from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = 'complete.pair.order'

    prescription = fields.Many2one('dr.prescription', string='Prescription')
    frame = fields.Many2one('product.product', string='Frames', domain="[('categ_id', '=', 'Frames')]")
    lens = fields.Many2one('product.product', string='Lens', domain="[('categ_id', '=', 'Lens')]")
    contact_lens = fields.Many2one('product.product', string='Contact Lens',
                                   domain="[('categ_id', '=', 'Contact Lens')]")
    lens_treatment = fields.Many2one('product.product', string='Lens Treatment',
                                     domain="[('categ_id', '=', 'Lens Treatment')]")
    service = fields.Many2one('product.product', string='Services', domain="[('categ_id', '=', 'Service')]")
    miscellaneous = fields.Many2one('product.product', string='Miscellaneous',
                                    domain="[('categ_id', '=', 'Miscellaneous')]")

    # sale_order_id = fields.Many2one('sale.order')

    def show_btn(self):
        SaleOrderLine = self.env['sale.order.line'].with_context(tracking_disable=True)
        section = 'Complete Pair Order' if self.env.context.get('is_complete_pair', False) else (
            'Contact Lens' if self.env.context.get('is_contact_lens', False) else (
                'Frame Only' if self.env.context.get('is_frame', False) else (
                    'Lens Only' if self.env.context.get('is_lens', False) else (
                        'Service' if self.env.context.get('is_services', False) else (
                            'Miscellaneous' if self.env.context.get('is_miscellaneous', False) else False
                        )
                    )
                )
            )
        )

        if section:
            SaleOrderLine.create({
                'name': section,
                'display_type': 'line_section',
                'order_id': self.env.context.get('active_id'),
            })

        for product in self.frame + self.lens_treatment + self.service + self.miscellaneous:
            sol_id = self.env['sale.order.line'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 1,
                'qty_delivered': 1,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
                'order_id': self.env.context.get('active_id'),
            })
            # sol_id._product_id_change()

        for product in self.lens + self.contact_lens:
            sol_id = self.env['sale.order.line'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 2,
                'qty_delivered': 1,
                'product_uom': product.uom_id.id,
                'price_unit': product.list_price,
                'order_id': self.env.context.get('active_id'),
            })
            # sol_id._product_id_change()
