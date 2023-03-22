# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_patient_conditions(models.Model):
    _name = 'medical.patient.conditions'
    _description = 'medical patient conditions'
    
    pathology_id = fields.Many2one('medical.pathology', 'Condition')
    is_active = fields.Boolean('Active Condition')
    diagnosed_date = fields.Date('Date of Diagnosis')
    age = fields.Date('Age when diagnosed')
    short_comment = fields.Char('Remarks')
    practitioner_id = fields.Many2one('medical.patient','Practitioner')
    date = fields.Date('Start of treatment')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    