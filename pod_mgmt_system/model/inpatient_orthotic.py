# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime


class inpatient_orthotic(models.Model):
    _name = "inpatient.orthotic"
    _description = "Inpatient orthotic"
    _rec_name = "medicament_id"

    medicament_id = fields.Many2one("medicament", string="Medicament", required=True)
    is_active = fields.Boolean(string="Active")
    start_treatment = fields.Datetime(string="Start Of Treatment", required=True)
    course_completed = fields.Boolean(string="Course Completed")
    inpatient_orthotic_physician_id = fields.Many2one("physician", string="Physician")
    pathology_id = fields.Many2one("pathology", string="Indication")
    end_treatment = fields.Datetime(string="End Of Treatment", required=True)
    discontinued = fields.Boolean(string="Discontinued")
    drug_route_id = fields.Many2one("drug.route", string=" Administration Route ")
    dose = fields.Float(string="Dose")
    qty = fields.Integer(string="X")
    dose_unit_id = fields.Many2one("dose.unit", string="Dose Unit")
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "hours"),
            ("days", "Days"),
            ("months", "Months"),
            ("years", "Years"),
            ("indefine", "Indefine"),
        ],
        string="Treatment Period",
    )
    orthotic_dosage_id = fields.Many2one("orthotic.dosage", string="Frequency")
    admin_times = fields.Char(string="Admin Hours")
    frequency = fields.Integer(string="frequency")
    frequency_unit = fields.Selection(
        [
            ("seconds", "Seconds"),
            ("minutes", "Minutes"),
            ("hours", "hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("wr", "When Required"),
        ],
        string="Unit",
    )
    adverse_reaction = fields.Text(string="Notes")
    inpatient_registration_id = fields.Many2one(
        "inpatient.registration", string="Orthotic"
    )
    inpatient_admin_times_ids = fields.One2many(
        "inpatient.orthotic.admin.time",
        "inpatient_admin_time_medicament_id",
        string="Admin",
    )
    inpatient_log_history_ids = fields.One2many(
        "inpatient.orthotic.log",
        "inaptient_log_medicament_id",
        string="Log History",
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
