# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_device(models.Model):
    _name = 'podiatry.patient.device'
    _description = 'podiatry patient device'
    _rec_name = 'podiatry_treatment_id'

    podiatry_treatment_id = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    treatment = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    podiatry_patient_device_id1 = fields.Many2one(
        'podiatry.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    doctor_physician_id = fields.Many2one(
        'podiatry.physician', string='Physician')
    pathology = fields.Many2one('podiatry.pathology', string='Pathology')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    route = fields.Many2one('podiatry.device.route',
                            string=" Administration Route ")
    quantity = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    podiatry_device_quantity_id = fields.Many2one(
        'podiatry.device.quantity', string='Quantity')
    quantity_unit = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unit')
    common_quantity = fields.Many2one(
        'podiatry.device.quantity', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    notes = fields.Text(string='Notes')
    podiatry_patient_device_id = fields.Many2one(
        'podiatry.patient', 'Patient')
    podiatry_patient_registration_id = fields.Many2one(
        'podiatry.patient.registration', string='Device')
    patient_admin_times_ids = fields.One2many(
        'podiatry.patient.device.admin.time', 'podiatry_patient_admin_time_treatment_id', string='Admin')
    patient_log_history_ids = fields.One2many(
        'podiatry.patient.device.log', 'podiatry_patient_log_treatment_id', string='Log History')

# sdfa
