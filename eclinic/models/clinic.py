from odoo import models, fields, api


class Clinic(models.Model):
    _name = 'clinic'
    _description = 'Clinic'

    name = fields.Char(string='Name', required=True)
    location = fields.Text(string='Description')

    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')

    doctors = fields.Many2many('eclinic.doctor', string='Doctors')
    patients = fields.One2many('eclinic.patient', 'clinic_id', string='Patients')
    pharmacies = fields.One2many('eclinic.pharmacist', 'clinic_id', string='Pharmacies')
    transactions = fields.One2many('eclinic.transaction', 'clinic_id', string='Transactions')
    appointments = fields.One2many('eclinic.appointment', 'clinic_id', string='Appointments')

    is_active = fields.Boolean(string='Active', default=True)
