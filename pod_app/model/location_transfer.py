# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date


class location_transfer(models.Model):
    _name = 'location.transfer'
    _description = "Location Transfer"

    name = fields.Char("Name")
    date = fields.Datetime(string='Date')
    location_from = fields.Char(string='From')
    location_to = fields.Char(string='To')
    reason = fields.Text(string='Reason')
    patient_id = fields.Many2one(
        'podiatry.patient.registration', string='Patient Id')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
