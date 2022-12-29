# -*- coding: utf-8 -*-

from odoo import models, fields


class CreateService(models.TransientModel):
    _name = 'create.service'
    _description = 'Create Service Wizard'

    visitation = fields.Many2one(
        'pet_clinic.visitation', string='visitation ID', required=True)
    service = fields.Many2one(
        'pet_clinic.item', string='Service', required=True, domain="[('item_type', '=', 'service')]")
    date_start = fields.Datetime(
        string='Date Start', required=True)
    date_end = fields.Datetime(
        string='Date End')

    def create_service(self):
        vals = {
            'visitation': self.visitation.id,
            'service': self.service,
            'date_start': self.date_start,
            'date_end': self.date_end
        }
        self.owner.message_post(
            body="Your New Service Has Been Added", subject="New Service")
        new_service = self.env['service_clinic.service'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'service_clinic.service',
                'res_id': new_service.id,
                'context': context
                }
