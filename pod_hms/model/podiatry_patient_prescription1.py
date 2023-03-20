# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_prescription1(models.Model):
    _name = 'podiatry.patient.prescription1'
    _description = 'podiatry patient prescription1'
    _rec_name = 'podiatry_patient_prescription_id'

    podiatry_treatment_id = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    podiatry_patient_prescription_id = fields.Many2one(
        'podiatry.patient', string='Prescription')
    is_active = fields.Boolean(string='Active', default=True)
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_practitioner_id = fields.Many2one(
        'podiatry.practitioner', string='Practitioner')
    indication_pathology_id = fields.Many2one(
        'podiatry.pathology', string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    product_route_id = fields.Many2one(
        'podiatry.product.route', string=" Administration Route ")
    quantity = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    quantity_unit_id = fields.Many2one(
        'podiatry.quantity.unit', string='Quantity Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'hours'),
                                        ('days', 'Days'),
                                        ('months', 'Months'),
                                        ('years', 'Years'),
                                        ('indefine', 'Indefine')], string='Treatment Period')
    prescription_quantity_id = fields.Many2one(
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


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
