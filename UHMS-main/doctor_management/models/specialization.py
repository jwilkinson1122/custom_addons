# models/specialization.py
from odoo import models, fields

class Specialization(models.Model):
    _name = 'hospital.specialization'
    _description = 'Specialization'
    
    name = fields.Char(string='Specialization Name', required=True)
    doctor_ids = fields.One2many('hospital.doctor', 'specialization_id', string='Doctors')
