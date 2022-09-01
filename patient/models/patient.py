# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Patient(models.Model):
    _name = "patient"
    _description = "Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Name")
    ref = fields.Char(string="Reference")
    devicecat_id = fields.Many2one(
        "patient.devicecat", string="Device Category", required=True)
    devicegroup_id = fields.Many2one(
        "patient.devicegroup", string="Device Group", required=True)
    devicetype_id = fields.Many2one("patient.devicetype", string="devicetype")
    size = fields.Char(string="Size")
    weight = fields.Float(string="Weight (in kg)")
    birth_date = fields.Date(string="Birth Date")
    gender = fields.Selection(
        string="Gender",
        selection=[
            ("female", "Female"),
            ("male", "Male"),
        ],
        # default="female",
        required=True,
    )
    active = fields.Boolean(default=True)
    image = fields.Binary(
        "Image", attachment=True, help="This field holds the photo of the patient."
    )

    @api.onchange("devicecat_id")
    def onchange_devicecat(self):
        self.devicegroup_id = False

    @api.onchange("devicegroup_id")
    def onchange_devicegroup(self):
        self.devicetype_id = False
