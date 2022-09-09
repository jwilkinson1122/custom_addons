from odoo import fields, models


class Practitioner(models.Model):
    _name = "practice.practitioner"
    _description = "Practice Practitioner"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    card_number = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
