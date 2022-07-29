# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class Device(models.Model):
    _name = "device"
    _description = "Device"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char()
    ref = fields.Char(string="Reference")
    category_id = fields.Many2one(
        "device.category", string="Category", required=True)
    type_id = fields.Many2one("device.type", string="Type", required=True)
    color_id = fields.Many2one("device.color", string="Color")
    size = fields.Char()
    weight = fields.Float(string="Weight (in kg)")
    birth_date = fields.Date()
    gender = fields.Selection(
        selection=[
            ("female", "Female"),
            ("male", "Male"),
            # ("hermaphrodite", "Hermaphrodite"),
            # ("neutered", "Neutered"),
        ],
        # default="female",
        required=True,
    )
    active = fields.Boolean(default=True)
    image = fields.Binary(
        attachment=True, help="This field holds the photo of the device."
    )

    @api.onchange("category_id")
    def onchange_category(self):
        self.type_id = False

    @api.onchange("type_id")
    def onchange_type(self):
        self.color_id = False
