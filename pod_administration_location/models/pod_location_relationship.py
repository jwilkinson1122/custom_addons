from odoo import fields, models


class PodLocationRelationship(models.Model):

    _name = "pod.location.relationship"
    _description = "Practice Location Relationship"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
