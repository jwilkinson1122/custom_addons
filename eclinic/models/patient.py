from odoo import models, fields, api


class Patient(models.Model):
    _name = 'eclinic.patient'
    _description = 'Patient'

    name = fields.Char(string='Patient Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    medical_history = fields.Text(string='Medical History')

    clinic_id = fields.Many2many('clinic', string='Clinic')
    appointments = fields.One2many('eclinic.appointment', 'patient_id', string='Appointments')
    insurance_id = fields.Many2one('eclinic.insurance', string='Patient Insurance')
