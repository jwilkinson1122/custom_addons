# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import time


class CreateVisitation(models.TransientModel):
    _name = 'create.visitation'
    _description = 'Create visitation Wizard'

    appointment = fields.Many2one(
        'pet_clinic.appointment')
    owner = fields.Many2one('pet_clinic.client',
                            required=True)
    pet = fields.Many2one(
        'pet_clinic.pet', required=True)
    doctor = fields.Many2one(
        'pet_clinic.doctor', required=True)
    date = fields.Datetime(string='Date', required=True)

    def create_visitation(self):
        vals = {
            'owner': self.owner.id,
            'pet': self.pet.id,
            'date': self.date,
            'doctor': self.doctor.id
        }
        self.appointment.message_post(
            body="new visitation Created", subject="visitation Creation")
        # creating visitations from the code
        new_visitation = self.env['pet_clinic.visitation'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pet_clinic.visitation',
                'res_id': new_visitation.id,
                'context': context
                }
