from odoo import models, fields


class PatientDiagnosis(models.Model):
    _name = "patient.diagnosis"
    _description = "Patient iagnosis"
    _order = "sequence,id"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Diagnosis",
        required=True,
        index=True,
        translate=True,
    )
    code = fields.Char(
        string="Code",
        copy=False,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
    )

    notes = fields.Text(
        string="Notes",
    )
