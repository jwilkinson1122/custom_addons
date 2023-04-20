# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class podiatry_medication_dosage(models.Model):
    _name = 'podiatry.medication.dosage'
    _description = 'podiatry medication dosage'
    
    name = fields.Char(string="Frequency",required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")

