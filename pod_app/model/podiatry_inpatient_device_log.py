# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import date, datetime


class podiatry_inpatient_device_log(models.Model):
    _name = 'podiatry.inpatient.device.log'
    _description = 'Podiatry Inpatient device Log'

    admin_time = fields.Datetime(string='Date', readonly=True)
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    podiatry_inpatient_device_log_id = fields.Many2one(
        'podiatry.physician', string='Health Professional', readonly=True)
    podiatry_dose_unit_id = fields.Many2one(
        'podiatry.dose.unit', string='Dose Unt')
    podiatry_inaptient_log_treatment_id = fields.Many2one(
        'podiatry.inpatient.device', string='Log History')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
