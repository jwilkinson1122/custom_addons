# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime

class podiatry_inpatient_medication_admin_time(models.Model):
    _name = 'podiatry.inpatient.medication.admin.time'
    _description = 'Podiatry Inpatient Medication Admin Time'

    admin_time = fields.Datetime(string='Date')
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    podiatry_inpatient_admin_time_id = fields.Many2one('podiatry.physician',string='Health Professional')
    dose_unit = fields.Many2one('podiatry.dose.unit',string='Dose Unt')
    podiatry_inpatient_admin_time_medicament_id = fields.Many2one('podiatry.inpatient.medication',string='Admin Time')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
