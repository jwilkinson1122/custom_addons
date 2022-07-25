# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime


class pod_patient_conditions(models.Model):
    _name = 'pod.patient.conditions'
    _description = 'pod patient conditions'

    pathelogh_id = fields.Many2one('pod.pathology', 'Condition')
    status_of_the_condition = fields.Selection([('healed', 'Healed'), (
        'improving', 'Improving'), ('worsening', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active Condition')
    diagnosed_date = fields.Date('Date of Diagnosis')
    condition_severity = fields.Selection(
        [('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')], 'Severity')
    short_comment = fields.Char('Remarks')
    doctor_id = fields.Many2one('pod.patient', 'Doctor')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
