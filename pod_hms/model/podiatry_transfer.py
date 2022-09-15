# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date


class podiatry_transfer(models.Model):
    _name = 'podiatry.transfer'
    _description = "Practice Transfer"

    name = fields.Char("Name")
    date = fields.Datetime(string='Date')
    practice_from = fields.Char(string='From')
    practice_to = fields.Char(string='To')
    reason = fields.Text(string='Reason')
    patient_id = fields.Many2one('podiatry.patient', string='Patient ID')
    # patient_id = fields.Many2one(
    #     'podiatry.patient.registration', string='Inpatient Id')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
