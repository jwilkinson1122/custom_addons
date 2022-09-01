# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientDeviceGroup(models.Model):
    _name = "patient.devicegroup"
    _description = "Patient Device Groups"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    devicecat_id = fields.Many2one(
        "patient.devicecat", string="Device Category", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
