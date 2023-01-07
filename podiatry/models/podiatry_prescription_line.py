# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class PrescriptionLine(models.Model):
    _name = "podiatry.prescription.line"
    _description = 'podiatry prescription line'
    _rec_name = 'product_id'

    @api.depends('product_id')
    def onchange_product(self):
        for each in self:
            if each:
                self.qty_available = self.product_id.qty_available
                self.price = self.product_id.lst_price
            else:
                self.qty_available = 0
                self.price = 0.0

    name = fields.Many2one('podiatry.prescription', 'Rx ID')
    prescription_id = fields.Many2one(
        "podiatry.prescription", "Prescription Number", ondelete="cascade")
    practitioner_id = fields.Many2one("podiatry.practitioner")
    practitioner = fields.Char(
        related='prescription_id.practitioner_id.name')
    patient_id = fields.Many2one("podiatry.patient")
    patient = fields.Char(
        related='prescription_id.patient_id.name')
    product_id = fields.Many2one('product.product', 'Name')
    foot_image1 = fields.Binary(related="patient_id.image1")
    foot_image2 = fields.Binary(related="patient_id.image2")
    left_obj_model = fields.Binary(related="patient_id.left_obj_model")
    right_obj_model = fields.Binary(related="patient_id.right_obj_model")

    field1 = fields.Char()
    field2 = fields.Char()
    field3 = fields.Char()

    @api.model
    def _selection_state(self):
        return [
            ('start', 'Start'),
            ('configure', 'Configure'),
            ('custom', 'Customize'),
            ('final', 'Final'),
        ]

    @api.model
    def _default_prescription_id(self):
        return self.env.context.get('active_id')

    def state_exit_start(self):
        self.state = 'configure'

    def state_exit_configure(self):
        self.state = 'custom'

    def state_exit_custom(self):
        self.state = 'final'

    def state_previous_custom(self):
        self.state = 'configure'

    def state_previous_final(self):
        self.state = 'custom'


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
