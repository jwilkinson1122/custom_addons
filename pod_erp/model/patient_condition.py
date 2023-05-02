# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from datetime import date,datetime
from odoo import api, fields, models, _


class patient_condition(models.Model):
    _name = "podiatry.patient.condition"
    _description = 'podiatry patient condition'
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one('podiatry.pathology','Condition', required=True)
    condition_severity =  fields.Selection([('1_mi','Mild'),
                               ('2_mo','Moderate'),
                               ('3_sv','Severe')],'Severity')
    status =  fields.Selection([('c','Chronic'),
                               ('s','Status quo'),
                               ('h','Healed'),
                               ('i','Improving'),
                               ('w','Worsening')],'Status of the condition')
    is_active = fields.Boolean('Active condition')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    age = fields.Integer('Age when diagnosed')
    doctor_id = fields.Many2one('podiatry.physician','Physician')
    is_allergic = fields.Boolean('Allergic Condition')
    allergy_type =  fields.Selection([('da','Drag Allergy'),
                               ('fa','Food Allergy'),
                               ('ma','Misc Allergy'),
                               ('mc','Misc Contraindication')],'Allergy type')
    is_on_treatment = fields.Boolean('Currently on Treatment')
    treatment_description = fields.Char('Treatment Description')
    patient_id = fields.Many2one('podiatry.patient',string="Patient")
    extra_info = fields.Text('info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: