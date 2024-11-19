# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime


class inpatient_orthotic_log(models.Model):
    _name = "inpatient.orthotic.log"
    _description = "Inpatient orthotic Log"

    admin_time = fields.Datetime(string="Date", readonly=True)
    dose = fields.Float(string="Dose")
    remarks = fields.Text(string="Remarks")
    inpatient_orthotic_log_id = fields.Many2one(
        "physician", string="Health Professional", readonly=True
    )
    dose_unit_id = fields.Many2one("dose.unit", string="Dose Unt")
    inaptient_log_medicament_id = fields.Many2one(
        "inpatient.orthotic", string="Log History"
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
