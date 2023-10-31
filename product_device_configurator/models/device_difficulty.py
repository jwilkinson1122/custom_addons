from odoo import fields, models


class DeviceDifficulty(models.Model):

    _name = 'device.difficulty'
    _description = "Device Difficulty Level"

    name = fields.Char(required=True)
    coefficient = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
