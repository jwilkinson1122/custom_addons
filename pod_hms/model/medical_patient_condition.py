# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from datetime import date,datetime
from odoo import api, fields, models, _


class medical_patient_condition(models.Model):
    _name = "medical.patient.condition"
    _description = 'medical patient condition'
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one('medical.pathology','Condition', required=True)
    condition_severity =  fields.Selection([('1_mi','Mild'),
                               ('2_mo','Moderate'),
                               ('3_sv','Severe')],'Severity')
    is_active = fields.Boolean('Active condition')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    age = fields.Integer('Age when diagnosed')
    practitioner_id = fields.Many2one('medical.practitioner','Practitioner')
    date = fields.Date('Start of treatment')
    patient_id = fields.Many2one('medical.patient',string="Patient")
    extra_info = fields.Text('info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: