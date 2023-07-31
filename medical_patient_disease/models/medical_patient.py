# -*- coding: utf-8 -*-
# Copyright 2008 Luis Falcon <lfalcon@gnusolidario.org>
# Copyright 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = 'medical.patient'

    disease_ids = fields.One2many(
        comodel_name='medical.patient.disease',
        inverse_name='patient_id',
        string='Diseases',
    )
    count_disease_ids = fields.Integer(
        compute='_compute_count_disease_ids',
        string='Diseases',
    )

    def _compute_count_disease_ids(self):
        for record in self:
            record.count_disease_ids = len(record.disease_ids)

    def action_invalidate(self):
        for record in self:
            record.active = False
            record.partner_id.active = False
            record.disease_ids.action_invalidate()

    def action_revalidate(self):
        for record in self:
            record.active = True
            record.partner_id.active = True
            disease_ids = self.env['medical.patient.disease'].search([
                ('patient_id', '=', self.id),
                ('active', '=', False),
            ])
            disease_ids.action_revalidate()
