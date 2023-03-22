# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_patient_device(models.Model):
    _name = 'medical.patient.device'
    _description = 'medical patient device'

    product = fields.Many2one('product.product',string='Product',required=True)
    medical_patient_device_id1 = fields.Many2one('medical.patient',string='Device')
    is_active = fields.Boolean(string='Active', default = True)
    prescription_date = fields.Datetime(string='Prescription Date',required=True)
    practitioner_practitioner_id = fields.Many2one('medical.practitioner',string='Practitioner')
    quantity = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    notes =fields.Text(string='Notes')
    medical_patient_device_id = fields.Many2one('medical.patient','Patient')
