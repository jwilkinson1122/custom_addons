# -*- coding: utf-8 -*-
# © 2016 LasLabs Inc.
# License GPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields, api


class MedicalPrescriptionOrderLine(models.Model):
    _inherit = 'medical.prescription.order.line'
    disease_id = fields.Many2one(
        string='Disease',
        comodel_name='medical.patient.disease',
        help='Disease diagnosis related to prescription.',
    )

    @api.onchange('patient_id')
    def _onchange_patient_id(self, ):
        self.ensure_one()
        return {
            'domain': {
                'disease_id': [('patient_id', '=', self.patient_id.id)],
                'prescription_order_id': [
                    ('patient_id', '=', self.patient_id.id)
                ],
            }
        }

    @api.onchange('disease_id')
    def _onchange_disease_id(self, ):
        for rec_id in self:
            rec_id.patient_id = rec_id.disease_id.patient_id.id
