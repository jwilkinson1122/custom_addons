from odoo import models, fields


class Occupation(models.Model):
    _name = 'hc.patient.occupation'
    _description = "Occupation"
    _order = 'name'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Occupation Title",
        required=True,
        index=True, translate=True,
    )
    code = fields.Char(
        string="Code",
        copy=False,
    )

    notes = fields.Text(
        string="Notes",
    )
