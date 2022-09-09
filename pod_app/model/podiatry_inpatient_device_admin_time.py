# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_inpatient_device_admin_time(models.Model):
    _name = 'podiatry.inpatient.device.admin.time'
    _description = 'Podiatry Inpatient Device Admin Time'

    admin_time = fields.Datetime(string='Date')
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    podiatry_inpatient_admin_time_id = fields.Many2one(
        'podiatry.physician', string='Health Professional')
    dose_unit = fields.Many2one('podiatry.dose.unit', string='Dose Unt')
    podiatry_inpatient_admin_time_treatment_id = fields.Many2one(
        'podiatry.inpatient.device', string='Admin Time')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
