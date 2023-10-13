from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = 'complete.pair.order'

    # prescription_order_id = fields.Many2one('pod.prescription.order')
    # prescription_order_line_id = fields.Many2one('pod.prescription.order.line')
    # practitioner_id = fields.Many2one(
    #     'pod.practitioner', string="Practitioner")
    # practitioner = fields.Char(
    #     string='Practitioner', related='practitioner_id.name')
    # patient_id = fields.Many2one(
    #     'pod.patient', string="Patient")

    prescription_order_id = fields.Many2one(
        'pod.prescription.order', string='Prescription(Rx)', required=True)
    practice_id = fields.Char(
        related='prescription_order_id.practice_id.name', required=True)
    practitioner_id = fields.Char(
        related='prescription_order_id.practitioner_id.name', required=True)
    patient_id = fields.Char(
        related='prescription_order_id.patient_id.name', required=True)

    sale = fields.Many2one('sale.order', default=lambda self: self.env.context.get('active_id'))
    customer_id = fields.Many2one(related='sale.partner_id')

    shell_foundation = fields.Many2one('product.product', string='Shell / Foundation',
                                       domain="[('categ_id', '=', 'Shell / Foundation')]", required=True)
    arch_height = fields.Many2one('product.product', string='Arch Height',
                                  domain="[('categ_id', '=', 'Arch Height')]", required=True)
    x_guard = fields.Many2one('product.product', string='X-Guard',
                              domain="[('categ_id', '=', 'X-Guard')]", required=True)
    top_cover = fields.Many2one('product.product', string='Top Cover',
                                domain="[('categ_id', '=', 'Top Cover')]", required=True)
    cushion = fields.Many2one('product.product', string='Cushion',
                              domain="[('categ_id', '=', 'Cushion')]", required=True)
    extension = fields.Many2one('product.product', string='Extension',
                                domain="[('categ_id', '=', 'Extension')]", required=True)

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
            'name': self.shell_foundation.name,
            'product_id': self.shell_foundation.id,
            'product_uom_qty': 1,
            'qty_delivered': 1,
            'product_uom': self.shell_foundation.uom_id.id,
            'price_unit': self.shell_foundation.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        SaleOrderLine.product_id_change()

        sale_order_line2 = self.env['sale.order.line'].create({
            'name': self.top_cover.name,
            'product_id': self.top_cover.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.top_cover.uom_id.id,
            'price_unit': self.top_cover.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line2.product_id_change()

        sale_order_line3 = self.env['sale.order.line'].create({
            'name': self.arch_height.name,
            'product_id': self.arch_height.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.arch_height.uom_id.id,
            'price_unit': self.arch_height.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line3.product_id_change()

        sale_order_line4 = self.env['sale.order.line'].create({
            'name': self.x_guard.name,
            'product_id': self.x_guard.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.x_guard.uom_id.id,
            'price_unit': self.x_guard.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line4.product_id_change()

        sale_order_line5 = self.env['sale.order.line'].create({
            'name': self.cushion.name,
            'product_id': self.cushion.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.cushion.uom_id.id,
            'price_unit': self.cushion.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line5.product_id_change()

        sale_order_line6 = self.env['sale.order.line'].create({
            'name': self.extension.name,
            'product_id': self.extension.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.extension.uom_id.id,
            'price_unit': self.extension.list_price,
            'order_id': self.env.context.get('active_id'),
        })
        sale_order_line6.product_id_change()

    # def show_btn_rx(self):
    #     PrescriptionOrderLine = self.env['pod.prescription.order.line'].with_context(
    #         tracking_disable=True)
    #     PrescriptionOrderLine.create({
    #         'name': 'Complete Pair Order',
    #         'display_type': 'line_section',
    #         'prescription_order_id': self.env.context.get('active_id'),
    #     })
    #     PrescriptionOrderLine = self.env['pod.prescription.order.line'].create({
    #         'name': self.frame.name,
    #         'product_id': self.frame.id,
    #         'product_uom_qty': 1,
    #         'qty_delivered': 1,
    #         'product_uom': self.frame.uom_id.id,
    #         'price_unit': self.frame.list_price,
    #         'order_id': self.env.context.get('active_id'),
    #     })
    #     PrescriptionOrderLine.product_id_change()

    #     sale_order_line2 = self.env['sale.order.line'].create({
    #         'name': self.lens.name,
    #         'product_id': self.lens.id,
    #         'product_uom_qty': 2,
    #         'qty_delivered': 1,
    #         'product_uom': self.lens.uom_id.id,
    #         'price_unit': self.lens.list_price,
    #         'order_id': self.env.context.get('active_id'),
    #     })
    #     sale_order_line2.product_id_change()
