# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class patient_orthotic1(models.Model):
    _name = "patient.orthotic1"
    _description = "pod patient orthotic1"
    _rec_name = "patient_orthotic_id"

    medicament_id = fields.Many2one("medicament", string="Medicament", required=True)
    patient_orthotic_id = fields.Many2one("patient", string="Orthotic")
    is_active = fields.Boolean(string="Active", default=True)
    start_treatment = fields.Datetime(string="Start Of Treatment", required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_physician_id = fields.Many2one("physician", string="Physician")
    indication_pathology_id = fields.Many2one("pathology", string="Indication")
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
    notes = fields.Text(string="Notes")


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
