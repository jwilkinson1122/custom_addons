# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class podiatry_patient_medication1(models.Model):
    _name = 'podiatry.patient.medication1'
    _description = 'podiatry patient medication1'
    _rec_name = 'podiatry_patient_medication_id'

    podiatry_medicament_id = fields.Many2one('podiatry.medicament',string='Medicament',required=True)
    podiatry_patient_medication_id = fields.Many2one('podiatry.patient',string='Medication')
    is_active = fields.Boolean(string='Active', default = True)
    start_treatment = fields.Datetime(string='Start Of Treatment',required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_physician_id = fields.Many2one('podiatry.physician',string='Physician')
    indication_pathology_id = fields.Many2one('podiatry.pathology',string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment',required=True)
    discontinued = fields.Boolean(string='Discontinued')
    drug_route_id = fields.Many2one('podiatry.drug.route',string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    dose_unit_id = fields.Many2one('podiatry.dose.unit',string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes','Minutes'),
                                        ('hours','hours'),
                                        ('days','Days'),
                                        ('months','Months'),
                                        ('years','Years'),
                                        ('indefine','Indefine')],string='Treatment Period')
    medication_dosage_id = fields.Many2one('podiatry.medication.dosage',string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),
                                       ('minutes','Minutes'),
                                       ('hours','hours'),
                                       ('days','Days'),
                                       ('weeks','Weeks'),
                                       ('wr','When Required')],string='Unit')
    notes =fields.Text(string='Notes')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
