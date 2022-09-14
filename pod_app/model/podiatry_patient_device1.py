# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_device1(models.Model):
    _name = 'podiatry.patient.device1'
    _description = 'podiatry patient device1'
    _rec_name = 'podiatry_patient_device_id'

    podiatry_treatment_id = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    podiatry_patient_device_id = fields.Many2one(
        'podiatry.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_physician_id = fields.Many2one(
        'podiatry.physician', string='Physician')
    pathology_pathology_id = fields.Many2one(
        'podiatry.pathology', string='Pathology')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    device_route_id = fields.Many2one(
        'podiatry.device.route', string=" Administration Route ")
    quantity = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    quantity_unit_id = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unit')
    device_quantity_id = fields.Many2one(
        'podiatry.device.quantity', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    notes = fields.Text(string='Notes')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
