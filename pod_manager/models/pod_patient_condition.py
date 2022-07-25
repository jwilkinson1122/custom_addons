# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import api, fields, models, _


class pod_patient_condition(models.Model):
    _name = "pod.patient.condition"
    _description = 'pod patient condition'
    _rec_name = 'pod_patient_id'

    pathology_id = fields.Many2one('pod.pathology', 'Condition', required=True)
    condition_severity = fields.Selection([('1_mi', 'Mild'),
                                           ('2_mo', 'Moderate'),
                                           ('3_sv', 'Severe')], 'Severity')
    status = fields.Selection([('h', 'Healed'),
                               ('i', 'Improving'),
                               ('w', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active condition')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    doctor_id = fields.Many2one('pod.doctor', 'Doctor')
    pod_patient_id = fields.Many2one('pod.patient', string="Patient")
    extra_info = fields.Text('info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
