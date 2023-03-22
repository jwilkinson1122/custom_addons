# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_patient_device1(models.Model):
    _name = 'medical.patient.device1'
    _description = 'medical patient device1'
    _rec_name = 'medical_patient_device_id'

    medical_product_id = fields.Many2one('product.product',string='Product',required=True)
    medical_patient_device_id = fields.Many2one('medical.patient',string='Device')
    is_active = fields.Boolean(string='Active', default = True)
    prescription_date = fields.Datetime(string='Start Of Treatment',required=True)
    practitioner_practitioner_id = fields.Many2one('medical.practitioner',string='Practitioner')
    pathology_id = fields.Many2one('medical.pathology',string='Indication')
    quantity = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    notes =fields.Text(string='Notes')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
