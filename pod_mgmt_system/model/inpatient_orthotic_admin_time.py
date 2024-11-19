# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime


class inpatient_orthotic_admin_time(models.Model):
    _name = "inpatient.orthotic.admin.time"
    _description = "Inpatient Orthotic Admin Time"

    admin_time = fields.Datetime(string="Date")
    dose = fields.Float(string="Dose")
    remarks = fields.Text(string="Remarks")
    inpatient_admin_time_id = fields.Many2one("physician", string="Health Professional")
    dose_unit = fields.Many2one("dose.unit", string="Dose Unt")
    inpatient_admin_time_medicament_id = fields.Many2one(
        "inpatient.orthotic", string="Admin Time"
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
