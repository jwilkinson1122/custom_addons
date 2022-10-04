from odoo import models, fields


class Weight(models.Model):
    _name = 'podiatry.patient.weight'
    _description = "Weight"
    _order = 'name'

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Weight Title",
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
