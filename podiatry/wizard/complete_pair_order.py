from odoo import models, api, fields


class CompletePairOrder(models.TransientModel):
    _name = 'complete.pair.order'

    prescription = fields.Many2one('podiatry.prescription', default=lambda self: self.env.context.get('active_id'))
    practice_id = fields.Many2one(related='prescription.practice_id')
    practitioner_id = fields.Many2one(related='prescription.practitioner_id')
    patient_id = fields.Many2one(related='prescription.patient_id')
    prescription = fields.Many2one('podiatry.prescription', string='Prescription(Rx)', required=True)
    shells = fields.Many2one('product.product', string='Shell / Foundation', domain="[('categ_id', '=', 'Shell / Foundation')]", required=True)
    top_covers = fields.Many2one('product.product', string='Top Covers', domain="[('categ_id', '=', 'Top Covers')]", required=True)

    # sale_prescription_id = fields.Many2one('sale.order')
    def show_btn(self):
        PrescriptionLine = self.env['podiatry.prescription.line'].with_context(tracking_disable=True)
        PrescriptionLine.create({
            'name': 'Complete Pair Order',
            'display_type': 'line_section',
            'prescription_id': self.env.context.get('active_id'),
        })
        PrescriptionLine = self.env['podiatry.prescription.line'].create({
            'name': self.frame.name,
            'product_id': self.frame.id,
            'product_uom_qty': 1,
            'qty_delivered': 1,
            'product_uom': self.frame.uom_id.id,
            'price_unit': self.frame.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        PrescriptionLine.product_id_change()

        prescription_line2 = self.env['podiatry.prescription.line'].create({
            'name': self.lens.name,
            'product_id': self.lens.id,
            'product_uom_qty': 2,
            'qty_delivered': 1,
            'product_uom': self.lens.uom_id.id,
            'price_unit': self.lens.list_price,
            'prescription_id': self.env.context.get('active_id'),
        })
        prescription_line2.product_id_change()
