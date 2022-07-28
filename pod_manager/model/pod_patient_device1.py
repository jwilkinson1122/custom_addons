# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class pod_patient_device1(models.Model):
    _name = 'pod.patient.device1'
    _description = 'podiatry patient device1'
    _rec_name = 'pod_patient_device_id'

    pod_treatment_id = fields.Many2one(
        'pod.treatment', string='Device', required=True)
    pod_patient_device_id = fields.Many2one(
        'pod.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)
    doctor_doctor_id = fields.Many2one(
        'pod.doctor', string='Doctor')
    qty = fields.Integer(string='X')
    notes = fields.Text(string='Notes')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
