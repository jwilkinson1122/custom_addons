from odoo import api, fields, models, _
from datetime import date, datetime


class pod_patient_device(models.Model):
    _name = 'pod.patient.device'
    _description = 'patient device'

    treatment = fields.Many2one(
        'pod.treatment', string='Treatment', required=True)
    pod_patient_device_id1 = fields.Many2one(
        'pod.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)

    pod_doctor_id = fields.Many2one(
        'pod.doctor', string='Doctor')
    diagnosis = fields.Many2one('pod.pathology', string='Diagnosis')

    qty = fields.Integer(string='X')

    notes = fields.Text(string='Notes')
    pod_patient_device_id = fields.Many2one('pod.patient', 'Patient')
