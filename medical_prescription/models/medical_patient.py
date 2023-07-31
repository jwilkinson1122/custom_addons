# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# Copyright 2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):

    _inherit = 'medical.patient'

    prescription_order_line_ids = fields.One2many(
        string='Prescriptions',
        comodel_name='medical.prescription.order.line',
        compute='_compute_prescription_order_line_ids_and_count',
    )
    prescription_order_line_count = fields.Integer(
        string='Prescription Line Count',
        compute='_compute_prescription_order_line_ids_and_count',
    )

    def _compute_prescription_order_line_ids_and_count(self):
        for record in self:
            OrderLine = self.env['medical.prescription.order.line']
            lines = OrderLine.search([
                ('patient_id', '=', record.id),
            ])
            record.prescription_order_line_count = len(lines)
            record.prescription_order_line_ids = [(6, 0, lines.ids)]
