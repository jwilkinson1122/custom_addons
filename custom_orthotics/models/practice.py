# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Practice(models.Model):
    _name = 'custom_orthotics.practice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    practice_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                              index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Integer(string='Age', required=True)
    image = fields.Binary(string='Image')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    prescription_count = fields.Integer(compute='compute_prescription_count')
    patient_count = fields.Integer(compute='compute_patient_count')

    # Item
    # item_service = fields.Many2many(
    #     'custom_orthotics.item', string='Service', domain="[('item_type', '=', 'service')]")

    @api.model
    def create(self, vals):
        if vals.get('practice_id', _('New')) == _('New'):
            vals['practice_id'] = self.env['ir.sequence'].next_by_code(
                'practice.seq') or _('New')
        result = super(Practice, self).create(vals)
        return result

    # Button Prescription Handle

    def open_practice_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('practice', '=', self.id)],
            'view_type': 'form',
            'res_model': 'custom_orthotics.prescription',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Count
    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['custom_orthotics.prescription'].search_count(
                [('practice', '=', self.id)])
