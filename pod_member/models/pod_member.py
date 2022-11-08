from odoo import fields, models


class Member(models.Model):
    _name = "pod.member"
    _description = "Podiatry Member"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    card_number = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
