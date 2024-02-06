# -*- coding: utf-8 -*-


from odoo import api, fields, models


class PrescriptionOrderCancel(models.TransientModel):
    _inherit = 'prescription.order.cancel'

    display_delivery_alert = fields.Boolean('Delivery Alert', compute='_compute_display_delivery_alert')

    @api.depends('order_id')
    def _compute_display_delivery_alert(self):
        for wizard in self:
            out_pickings = wizard.order_id.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing')
            wizard.display_delivery_alert = bool(any(picking.state == 'done' for picking in out_pickings))
