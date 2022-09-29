from odoo import models, fields


class Type(models.Model):
    _name = 'hc.type'
    _description = "Type"

    active = fields.Boolean(
        string="Active",
        default=True,
    )
    name = fields.Char(
        string="Type Name",
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

    company_id = fields.Many2one(
        comodel_name='res.company',
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
