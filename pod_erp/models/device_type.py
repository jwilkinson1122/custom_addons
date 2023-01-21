from odoo import api, fields, models, _


class TestType(models.Model):
    _name = 'device.type'
    _rec_name = 'name'

    name = fields.Char(string='Test_type', required=True)
