# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PatientDeviceCategories(models.Model):
    _name = "patient.devicecat"
    _description = "Patient Device Categories"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    devicegroup_ids = fields.One2many(
        "patient.devicegroup", "devicecat_id", string="Device Groups")
