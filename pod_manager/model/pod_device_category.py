from odoo import fields, models


class DeviceCategory(models.Model):
    _name = "device.category"
    _description = "Device Categories"
    _order = "name"

    name = fields.Char(string="Name", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
    device_type_ids = fields.One2many(
        "device.type", "device_category_id", string="Device Types")
