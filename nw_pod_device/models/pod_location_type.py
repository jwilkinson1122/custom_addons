from odoo import fields, models


class PodiatryLocationType(models.Model):
    _name = "pod.location.type"
    _description = "pod.location.type"

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(required=True, default=True)
