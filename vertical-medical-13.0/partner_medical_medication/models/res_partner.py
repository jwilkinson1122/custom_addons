# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    medication_ids = fields.Many2many(
        string='Medications',
        comodel_name='medical.patient.medication',
        compute='_compute_medication_ids_and_count',
    )
    count_medications = fields.Integer(
        compute='_compute_medication_ids_and_count',
    )

    @api.depends('patient_ids', 'patient_ids.medication_ids')
    def _compute_medication_ids_and_count(self):
        for record in self:
            medications = record.patient_ids.mapped('medication_ids')
            record.medication_ids = [(6, 0, medications.ids)]
            record.count_medications = len(medications)
