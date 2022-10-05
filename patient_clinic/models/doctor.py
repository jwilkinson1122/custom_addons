# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Doctor(models.Model):
    _name = 'patient_clinic.doctor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    doctor_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                            index=True, default=lambda self: _('New'))
    name = fields.Char(string="Name", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Integer(string='Age', required=True)
    image = fields.Binary(string='Image', attachment=True)
    phone = fields.Char(string='Phone', required=True)
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    # Patient
    patient = fields.One2many('patient_clinic.patient',
                              'owner', string='Patient')
    patient_count = fields.Integer(compute='compute_patient_count')

    # Prescription
    prescription_count = fields.Integer(compute='compute_prescription_count')

    # Item
    item_service = fields.Many2many(
        'patient_clinic.item', string='Service', domain="[('item_type', '=', 'service')]")

    @api.model
    def create(self, vals):
        if vals.get('doctor_id', _('New')) == _('New'):
            vals['doctor_id'] = self.env['ir.sequence'].next_by_code(
                'doctor.seq') or _('New')
        result = super(Doctor, self).create(vals)
        return result

    # Button Patient Handle
    def open_doctor_patient(self):
        return {
            'name': _('Patients'),
            'domain': [('doctor', '=', self.id)],
            'view_type': 'form',
            'res_model': 'patient_clinic.patient',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_patient_count(self):
        for record in self:
            record.patient_count = self.env['patient_clinic.patient'].search_count(
                [('doctor', '=', self.id)])

    # Button Prescription Handle
    def open_doctor_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('owner_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'patient_clinic.prescription',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
        }

    # Button Prescription Count
    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['patient_clinic.prescription'].search_count(
                [('owner_id', '=', self.id)])
