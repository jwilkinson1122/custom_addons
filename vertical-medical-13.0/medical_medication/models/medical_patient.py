# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    medication_ids = fields.One2many(
        string='Medications',
        comodel_name='medical.patient.medication',
        inverse_name='patient_id',
        help='Medications that the patient is currently on',
    )

    count_medication_ids = fields.Integer(
        compute='_compute_count_medication_ids',
        string='Medications',
    )

    def _compute_count_medication_ids(self):
        for rec_id in self:
            rec_id.count_medication_ids = len(rec_id.medication_ids)
