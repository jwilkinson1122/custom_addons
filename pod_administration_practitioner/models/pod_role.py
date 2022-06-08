

from odoo import fields, models


class PodRole(models.Model):

    _name = "pod.role"
    _description = "Practitioner Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
