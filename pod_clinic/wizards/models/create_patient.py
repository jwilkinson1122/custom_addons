# -*- coding: utf-8 -*-

from odoo import models, fields


class CreatePatient(models.TransientModel):
    _name = 'create.patient'
    _description = 'Create Patient Wizard'

    owner = fields.Many2one(
        'pod_clinic.practice', string="Owner", required=True)
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)

    def create_patient(self):
        vals = {
            'owner': self.owner.id,
            'name': self.name,
            'gender': self.gender
        }
        self.owner.message_post(
            body="Your New Patient Has Been Added", subject="New Patient")
        new_patient = self.env['pod_clinic.patient'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pod_clinic.patient',
                'res_id': new_patient.id,
                'context': context
                }
