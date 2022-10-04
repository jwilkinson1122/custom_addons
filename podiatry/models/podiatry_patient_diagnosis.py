from odoo import models, fields


class Diagnosis(models.Model):
    _name = 'podiatry.patient.diagnosis'
    _description = "Diagnosis"
    _order = 'sequence,id'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Diagnosis Title",
        required=True,
        index=True, translate=True,
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
