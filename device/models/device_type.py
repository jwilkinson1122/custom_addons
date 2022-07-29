# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class DeviceType(models.Model):
    _name = "device.type"
    _description = "Device Types"
    _order = "name"

    name = fields.Char(translate=True)
    category_id = fields.Many2one(
        "device.category", string="Category", required=True)
