
from odoo import api, fields, models


class Doctor(models.Model):
    _name = "hospital.doctor"
    _description = "Hospital Doctor"


    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', )
    patient_ids = fields.Many2many('hospital.patient', 'doctor_patient_rel', string="Patients")