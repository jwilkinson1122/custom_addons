# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_prescription(models.Model):
    _name = 'podiatry.patient.prescription'
    _description = 'podiatry patient prescription'

    treatment = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    podiatry_patient_prescription_id1 = fields.Many2one(
        'podiatry.patient', string='Device')
    is_active = fields.Boolean(string='Active', default=True)
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_practitioner_id = fields.Many2one(
        'podiatry.practitioner', string='Practitioner')
    indication = fields.Many2one('podiatry.pathology', string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    route = fields.Many2one('podiatry.product.route',
                            string=" Administration Route ")
    quantity = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    quantity_unit = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'hours'),
                                        ('days', 'Days'),
                                        ('months', 'Months'),
                                        ('years', 'Years'),
                                        ('indefine', 'Indefine')], string='Treatment Period')
    common_quantity = fields.Many2one(
        'podiatry.prescription.quantity', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'),
                                       ('minutes', 'Minutes'),
                                       ('hours', 'hours'),
                                       ('days', 'Days'),
                                       ('weeks', 'Weeks'),
                                       ('wr', 'When Required')], string='Unit')
    notes = fields.Text(string='Notes')
    podiatry_patient_prescription_id = fields.Many2one(
        'podiatry.patient', 'Patient')
