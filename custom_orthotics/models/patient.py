# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Patient(models.Model):
    _name = 'custom_orthotics.patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rec_name'

    patient_id = fields.Char(string='ID', required=True, copy=False, readonly=True,
                             index=True, default=lambda self: _('New'))
    name = fields.Char(string='Name', required=True)
    rec_name = fields.Char(string='Recname',
                           compute='_compute_fields_rec_name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
    ], default='male', string="Gender", required=True)
    age = fields.Char(string='Age')
    image = fields.Binary(string='Image')
    description = fields.Text(string='Description')

    # Patient -> Type
    patient_type = fields.Many2one('custom_orthotics.patient.type',
                                   string='Species')
    patient_type_name = fields.Char(related='patient_type.name',
                                    string='Species')

    # Patient -> Breed
    patient_breed = fields.Many2one('custom_orthotics.patient.breed', domain="[('patient_type','=',patient_type)]",
                                    string='Breed')
    patient_breed_name = fields.Char(related='patient_breed.name',
                                     string='Breed')

    # Owner
    owner = fields.Many2one(
        'custom_orthotics.doctor', string='Owner', store=True, readonly=False)
    owner_id = fields.Integer(
        related='owner.id', string='Patient Owner ID')
    owner_name = fields.Char(
        related='owner.name', string='Owner Name')

    # Prescription
    prescription_count = fields.Integer(compute='compute_prescription_count')

    @api.depends('name', 'patient_type_name', 'patient_breed_name')
    def _compute_fields_rec_name(self):
        for patient in self:
            if(patient.patient_type_name == False and patient.patient_breed_name == False):
                patient.rec_name = '{}'.format(patient.name)
            elif(patient.patient_breed_name == False):
                patient.rec_name = '{} - {}'.format(patient.name,
                                                    patient.patient_type_name)
            elif(patient.patient_type_name == False):
                patient.rec_name = '{}'.format(patient.name)
            else:
                patient.rec_name = '{} - {} {}'.format(patient.name,
                                                       patient.patient_type_name, patient.patient_breed_name)

    @api.model
    def create(self, vals):
        if vals.get('patient_id', _('New')) == _('New'):
            vals['patient_id'] = self.env['ir.sequence'].next_by_code(
                'patient.seq') or _('New')
        result = super(Patient, self).create(vals)
        return result

    # Button Patient Handle

    def open_patient_prescription(self):
        return {
            'name': _('Prescriptions'),
            'domain': [('patient', '=', self.id)],
            'view_type': 'form',
            'res_model': 'custom_orthotics.prescription',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    # Button Patient Count

    def compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['custom_orthotics.prescription'].search_count(
                [('patient', '=', self.id)])


class PatientType(models.Model):
    _name = 'custom_orthotics.patient.type'
    name = fields.Char(string='Name', required=True)


class PatientBreed(models.Model):
    _name = 'custom_orthotics.patient.breed'
    name = fields.Char(string='Name', required=True)
    patient_type = fields.Many2one('custom_orthotics.patient.type',
                                   string='Type', required=True)
