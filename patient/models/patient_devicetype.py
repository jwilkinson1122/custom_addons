# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientDeviceType(models.Model):
    _name = "patient.devicetype"
    _description = "Patient Device Types"

    name = fields.Char(string="Name", translate=True)
    devicegroup_id = fields.Many2one(
        "patient.devicegroup", string="Device Group", required=True)
    devicecat_id = fields.Many2one(
        "patient.devicecat", string="Device Category", related="devicegroup_id.devicecat_id", readonly=True
    )
