# -*- coding: utf-8 -*-

from odoo import models, fields


class CreatePrescription(models.TransientModel):
    _name = 'create.prescription'
    _description = 'Create Prescription Wizard'

    # practitioner_id = fields.Many2one(
    #     comodel_name='podiatry.practitioner',
    #     string='Practitioner')

    practitioner_id = fields.Many2one(
        'podiatry.practitioner', string="Practitioner", required=True)
    # name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one('product.product', 'Name')

    def create_prescription(self):
        vals = {
            'practitioner_id': self.practitioner_id.id,
            'product_id': self.product_id.id,
            # 'name': self.name,
        }
        self.practitioner_id.message_post(
            body="Your New Prescription Has Been Added", subject="New Prescription")
        new_prescription = self.env['podiatry.prescription'].create(vals)
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'podiatry.prescription',
                'res_id': new_prescription.id,
                'context': context
                }
