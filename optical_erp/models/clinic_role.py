from odoo import fields, models


class ClinicRole(models.Model):

    _name = "clinic.role"
    _description = "Clinic User Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
