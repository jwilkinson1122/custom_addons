from odoo import models, fields


class Education(models.Model):
    _name = 'hc.patient.education'
    _description = "Education"
    _order = 'sequence,id'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Education Title",
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
