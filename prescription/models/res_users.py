

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    prescription_team_id = fields.Many2one(
        comodel_name="prescription.team",
        string="Prescription Team",
        help="Prescription Team the user is member of.",
    )
