# -*- coding: utf-8 -*-


from datetime import date, datetime
from odoo import api, fields, models, _


class pod_patient_condition(models.Model):
    _name = "pod.patient.condition"
    _description = 'podiatry patient condition'
    _rec_name = 'patient_id'

    pathology_id = fields.Many2one(
        'pod.pathology', 'Pathology', required=True)
    # condition_severity = fields.Selection([('1_mi', 'Mild'),
    #                                        ('2_mo', 'Moderate'),
    #                                        ('3_sv', 'Severe')], 'Severity')
    is_active = fields.Boolean('Active condition')
    short_comment = fields.Char('Remarks')
    doctor_id = fields.Many2one('pod.doctor', 'Doctor')
    patient_id = fields.Many2one('pod.patient', string="Patient")
    extra_info = fields.Text('info')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
