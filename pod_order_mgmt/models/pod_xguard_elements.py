from odoo import models, api, fields


class XGuardLength(models.Model):
    _name = "x_guard.length"

    name = fields.Char(required=True)
