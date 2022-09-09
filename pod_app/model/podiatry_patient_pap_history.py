# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_pap_history(models.Model):

    _name = 'podiatry.patient.pap.history'
    _description = 'podiatry patient pap history'

    patient_id = fields.Many2one('podiatry.patient', 'Patient')
    evolution_id = fields.Many2one('podiatry.patient.evaluation', 'Evaluation')
    evolution_date = fields.Datetime('Evaluation Date')
    result = fields.Selection([('negative', 'Negative'),
                               ('c1', 'ASC-US'),
                               ('c2', 'ASC-H'),
                               ('g1', 'ASG'),
                               ('c3', 'LSIL'),
                               ('c4', 'HISL'),
                               ('g4', 'AIS')], 'Result')
    remark = fields.Char('Remark')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
