# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import time


class CreateOrder(models.TransientModel):
    _name = 'create.order'
    _description = 'Create order Wizard'

    prescription = fields.Many2one('custom_orthotics.prescription')
    owner = fields.Many2one('custom_orthotics.doctor', required=True)
    patient = fields.Many2one('custom_orthotics.patient', required=True)
    practice = fields.Many2one('custom_orthotics.practice', required=True)
    date = fields.Datetime(string='Date', required=True)

    def create_order(self):
        vals = {
            'owner': self.owner.id,
            'patient': self.patient.id,
            'date': self.date,
            'practice': self.practice.id
        }
        self.prescription.message_post(
            body="new order Created", subject="order Creation")
        # creating orders from the code
        new_order = self.env['custom_orthotics.order'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'custom_orthotics.order',
                'res_id': new_order.id,
                'context': context
                }
