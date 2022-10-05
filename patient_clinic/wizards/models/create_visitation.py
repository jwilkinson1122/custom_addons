# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import time


class CreateVisitation(models.TransientModel):
    _name = 'create.visitation'
    _description = 'Create visitation Wizard'

    prescription = fields.Many2one(
        'patient_clinic.prescription')
    owner = fields.Many2one('patient_clinic.doctor',
                            required=True)
    patient = fields.Many2one(
        'patient_clinic.patient', required=True)
    doctor = fields.Many2one(
        'patient_clinic.doctor', required=True)
    date = fields.Datetime(string='Date', required=True)

    def create_visitation(self):
        vals = {
            'owner': self.owner.id,
            'patient': self.patient.id,
            'date': self.date,
            'doctor': self.doctor.id
        }
        self.prescription.message_post(
            body="new visitation Created", subject="visitation Creation")
        # creating visitations from the code
        new_visitation = self.env['patient_clinic.visitation'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'patient_clinic.visitation',
                'res_id': new_visitation.id,
                'context': context
                }
