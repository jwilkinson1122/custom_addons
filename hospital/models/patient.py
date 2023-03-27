from odoo import api, fields, models


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Pasient'

    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'), 
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default="other")
    note = fields.Text('Description')
    
    
