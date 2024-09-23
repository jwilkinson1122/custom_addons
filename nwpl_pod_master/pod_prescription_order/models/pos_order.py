# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    prescription_order_id = fields.Many2one('prescription.order', string='Prescription Ref', help="Prescription order reference for the pos order")

    @api.model
    def _order_fields(self, ui_order):
        """Overriding to pass value of prescription order ref to PoS order
           ui_order(dict): dictionary of pos order field values
           dict: returns dictionary of pos order field values
        """
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('is_prescription'):
            order_fields['prescription_order_id'] = ui_order.get('prescription_data')['id']
            self.env['prescription.order'].browse(
                ui_order.get('prescription_data')['id']).write(
                {'state': 'confirmed'})
        return order_fields