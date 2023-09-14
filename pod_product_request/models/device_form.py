# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeviceForm(models.Model):

    _name = "device.form"
    _description = "Device Form"

    name = fields.Char()

    uom_ids = fields.Many2many("uom.uom")
