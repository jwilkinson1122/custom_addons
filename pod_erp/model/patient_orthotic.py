# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class patient_orthotic(models.Model):
    _name = 'podiatry.patient.orthotic'
    _description = 'podiatry patient orthotic'

    orthotic = fields.Many2one('podiatry.orthotic',string='Orthotic',required=True)
    patient_orthotic_id = fields.Many2one('podiatry.patient','Patient')
    patient_orthotic_id1 = fields.Many2one('podiatry.patient',string='Orthotic')
    is_active = fields.Boolean(string='Active', default = True)
    prescription_datee = fields.Datetime(string='Prescription Date')
    doctor_physician_id = fields.Many2one('podiatry.physician',string='Physician')
    indication = fields.Many2one('podiatry.pathology',string='Indication')
    route = fields.Many2one('podiatry.device.route',string=" Administration Route ")
    quant = fields.Float(string='Quantity')
    qty = fields.Integer(string='X')
    quant_unit = fields.Many2one('podiatry.quant.unit',string='Quantity Unit')
    common_measure = fields.Many2one('podiatry.orthotic.measure',string='Frequency')
    notes =fields.Text(string='Notes')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes','Minutes'),
                                        ('hours','hours'),
                                        ('days','Days'),
                                        ('months','Months'),
                                        ('years','Years'),
                                        ('indefine','Indefine')],string='Treatment Period')
    orthotic_measure_id = fields.Many2one('podiatry.orthotic.measure',string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),
                                       ('minutes','Minutes'),
                                       ('hours','hours'),
                                       ('days','Days'),
                                       ('weeks','Weeks'),
                                       ('wr','When Required')],string='Unit')