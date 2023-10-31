from odoo import fields, models


class DeviceDie(models.Model):

    _name = 'device.die'
    _description = "Device Die Type"

    name = fields.Char(required=True)
    # Optional if it needs to be included in generated product code.
    code = fields.Char()
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
