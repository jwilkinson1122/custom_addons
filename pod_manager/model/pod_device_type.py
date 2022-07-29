from odoo import fields, models


class DeviceType(models.Model):
    _name = "device.type"
    _description = "Device Types"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    species_id = fields.Many2one(
        "device_category_id", string="Device Categories", required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
