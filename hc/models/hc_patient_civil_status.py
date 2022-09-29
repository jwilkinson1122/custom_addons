from odoo import models, fields


class CivilStatus(models.Model):
    _name = 'hc.patient.civil_status'
    _description = "Civil Status"
    _order = 'sequence,id'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Description",
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
