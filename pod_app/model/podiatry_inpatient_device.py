# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_inpatient_device(models.Model):
    _name = 'podiatry.inpatient.device'
    _description = 'Podiatry Inpatient device'
    _rec_name = 'podiatry_treatment_id'

    podiatry_treatment_id = fields.Many2one(
        'podiatry.treatment', string='Treatment', required=True)
    is_active = fields.Boolean(string='Active')
    start_treatment = fields.Datetime(
        string='Start Of Treatment', required=True)
    course_completed = fields.Boolean(string="Course Completed")
    podiatry_inpatient_device_physician_id = fields.Many2one(
        'podiatry.physician', string='Physician')
    podiatry_pathology_id = fields.Many2one(
        'podiatry.pathology', string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment', required=True)
    discontinued = fields.Boolean(string='Discontinued')
    podiatry_drug_route_id = fields.Many2one(
        'podiatry.drug.route', string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    podiatry_dose_unit_id = fields.Many2one(
        'podiatry.dose.unit', string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes', 'Minutes'),
                                        ('hours', 'hours'),
                                        ('days', 'Days'),
                                        ('months', 'Months'),
                                        ('years', 'Years'),
                                        ('indefine', 'Indefine')], string='Treatment Period')
    podiatry_device_dosage_id = fields.Many2one(
        'podiatry.device.dosage', string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds', 'Seconds'),
                                       ('minutes', 'Minutes'),
                                       ('hours', 'hours'),
                                       ('days', 'Days'),
                                       ('weeks', 'Weeks'),
                                       ('wr', 'When Required')], string='Unit')
    adverse_reaction = fields.Text(string='Notes')
    podiatry_inpatient_registration_id = fields.Many2one(
        'podiatry.inpatient.registration', string='Device')
    inpatient_admin_times_ids = fields.One2many(
        'podiatry.inpatient.device.admin.time', 'podiatry_inpatient_admin_time_treatment_id', string='Admin')
    inpatient_log_history_ids = fields.One2many(
        'podiatry.inpatient.device.log', 'podiatry_inaptient_log_treatment_id', string='Log History')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
