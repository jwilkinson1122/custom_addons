# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class podiatry_patient_rounding_vaccine(models.Model):
    _name = 'podiatry.patient.rounding.vaccine'
    _description = 'podiatry patient rounding vaccine'
    
    vaccine_id = fields.Many2one('product.product',string="Vaccines",required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.production.lot',string='Lot',required=True)
    dose = fields.Integer(string="Dose")
    next_dose_date = fields.Datetime(string="Next Dose")
    short_comment = fields.Char(string='Comment')
    podiatry_patient_rounding_vaccine_id = fields.Many2one('podiatry.patient.rounding',string="Vaccines")

