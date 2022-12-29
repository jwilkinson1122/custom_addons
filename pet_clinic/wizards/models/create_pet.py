# -*- coding: utf-8 -*-

from odoo import models, fields


class CreatePet(models.TransientModel):
    _name = 'create.pet'
    _description = 'Create Pet Wizard'

    owner = fields.Many2one(
        'pet_clinic.client', string="Owner", required=True)
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)

    def create_pet(self):
        vals = {
            'owner': self.owner.id,
            'name': self.name,
            'gender': self.gender
        }
        self.owner.message_post(
            body="Your New Pet Has Been Added", subject="New Pet")
        new_pet = self.env['pet_clinic.pet'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'pet_clinic.pet',
                'res_id': new_pet.id,
                'context': context
                }
