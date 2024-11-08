from odoo import fields, models


class RepairTeam(models.Model):
    """Model for creating repair team and assigns repair requests to each team"""

    _name = "repair.team"
    _description = "Repair Team"

    name = fields.Char(string="Team Name", help="Name Of the Team")
    team_head_id = fields.Many2one(
        "res.users", string="Team Head", help="Choose the Team Head"
    )
    member_ids = fields.Many2one("res.users", string="Member")
