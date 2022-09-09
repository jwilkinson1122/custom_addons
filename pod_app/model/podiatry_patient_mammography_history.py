# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from datetime import date, datetime


class podiatry_patient_mammography_history(models.Model):

    _name = 'podiatry.patient.mammography.history'
    _description = 'podiatry patient mammography history'

    patient_id = fields.Many2one('podiatry.patient', 'Patient')
    evolution_id = fields.Many2one('podiatry.patient.evaluation', 'Evaluation')
    evolution_date = fields.Date('Date')
    last_mamography_date = fields.Date('Date')
    result = fields.Selection([('normal', 'Normal'), ('abnormal', 'Abnormal')])
    remark = fields.Char('Comments')


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
