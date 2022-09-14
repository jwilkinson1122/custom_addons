# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_conditions(models.Model):
    _name = 'podiatry.patient.conditions'
    _description = 'podiatry patient conditions'

    pathelogh_id = fields.Many2one('podiatry.pathology', 'Condition')
    status_of_the_condition = fields.Selection(
        [('improving', 'Improving'), ('worsening', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active Condition')
    diagnosed_date = fields.Date('Date of Diagnosis')
    age = fields.Date('Age')
    condition_severity = fields.Selection(
        [('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], 'Severity')
    short_comment = fields.Char('Remarks')
    physician_id = fields.Many2one('podiatry.patient', 'Doctor')
    has_device = fields.Boolean('Currently has orthotic device')
    treatment_description = fields.Char('Treatment Description')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
