# -*- coding: utf-8 -*-


from datetime import date, datetime
from odoo import api, fields, models, _


class podiatry_patient_condition(models.Model):
    _name = "podiatry.patient.condition"
    _description = 'podiatry patient condition'
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one(
        'podiatry.pathology', 'Condition', required=True)
    condition_severity = fields.Selection([('1_mi', 'Mild'),
                                           ('2_mo', 'Moderate'),
                                           ('3_sv', 'Severe')], 'Severity')
    status = fields.Selection([('i', 'Improving'),
                               ('w', 'Worsening')], 'Status of the condition')
    is_active = fields.Boolean('Active condition')
    short_comment = fields.Char('Remarks')
    diagnosis_date = fields.Date('Date of Diagnosis')
    age = fields.Integer('Age when diagnosed')
    doctor_id = fields.Many2one('podiatry.physician', 'Physician')
    has_device = fields.Boolean('Currently has orthotic device')
    treatment_description = fields.Char('Treatment Description')
    patient_id = fields.Many2one('podiatry.patient', string="Patient")
    extra_info = fields.Text('info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
