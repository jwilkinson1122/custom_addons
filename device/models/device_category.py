# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class DeviceCategory(models.Model):
    _name = "device.category"
    _description = "Device Category"
    _order = "name"

    name = fields.Char(translate=True)
    type_ids = fields.One2many("device.type", "category_id", string="Types")
