from odoo import api, fields, models, _


class DeviceType(models.Model):
    _name = 'orthotic.device.type'
    _rec_name = 'name'

    name = fields.Char(string='Device Type', required=True)
