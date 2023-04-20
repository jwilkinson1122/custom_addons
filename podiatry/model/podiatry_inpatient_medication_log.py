# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime

class podiatry_inpatient_medication_log(models.Model):
    _name = 'podiatry.inpatient.medication.log'
    _description = 'Podiatry Inpatient medication Log'

    admin_time = fields.Datetime(string='Date',readonly=True)
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    podiatry_inpatient_medication_log_id = fields.Many2one('podiatry.physician',string='Health Professional',readonly=True)
    podiatry_dose_unit_id = fields.Many2one('podiatry.dose.unit',string='Dose Unt')
    podiatry_inaptient_log_medicament_id = fields.Many2one('podiatry.inpatient.medication',string='Log History')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
