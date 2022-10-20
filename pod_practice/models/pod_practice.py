from odoo import fields, models


class Practice(models.Model):
    _name = "pod.practice"
    _description = "Podiatry Practice"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    card_number = fields.Char()
    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
