# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class DeviceColor(models.Model):
    _name = "device.color"
    _description = "Device Colors"

    name = fields.Char(translate=True)
    type_id = fields.Many2one("device.type", string="Type", required=True)
    category_id = fields.Many2one(
        "device.category", string="Category", related="type_id.category_id", readonly=True
    )
