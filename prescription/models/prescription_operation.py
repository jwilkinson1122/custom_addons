

from odoo import fields, models


class PrescriptionOperation(models.Model):
    _name = "prescription.operation"
    _description = "Prescription requested operation"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "That operation name already exists !"),
    ]
