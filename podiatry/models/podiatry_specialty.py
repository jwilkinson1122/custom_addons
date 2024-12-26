from odoo import models, fields


class Specialty(models.Model):
    _name = "podiatry.specialty"
    _description = "specialty"

    name = fields.Char()

    active = fields.Boolean(default=True)

    parent_id = fields.Many2one(
        comodel_name="podiatry.specialty",
        string="Parent Category",
        index=True,
        ondelete="cascade",
    )
