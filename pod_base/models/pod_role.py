from odoo import fields, models


class PodiatryRole(models.Model):
    _name = "pod.role"
    _description = "Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
