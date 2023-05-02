# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class patient_conditions(models.Model):
    _name = 'podiatry.patient.conditions'
    _description = 'podiatry patient conditions'
    
    pathology_id = fields.Many2one('podiatry.pathology', 'Condition')
    status_of_the_condition = fields.Selection([('chronic','Chronic'),('status quo','Status Quo'),('healed','Healed'), ('improving','Improving'), ('worsening', 'Worsening') ], 'Status of the condition')
    is_active = fields.Boolean('Active Condition')
    diagnosed_date = fields.Date('Date of Diagnosis')
    age = fields.Date('Age when diagnosed')
    condition_severity = fields.Selection([('mild','Mild'), ('moderate','Moderate'), ('severe','Severe')], 'Severity')
    short_comment = fields.Char('Remarks')
    physician_id = fields.Many2one('podiatry.patient','Doctor')
    is_allergy = fields.Boolean('Allergic Condition')
    allergy_type  = fields.Selection([('device_allergy', 'Device Allergy'),('food_allergy', 'Food Allergy'),('misc', 'Misc')], 'Allergy_type')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    