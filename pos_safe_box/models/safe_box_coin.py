from odoo import fields, models


class SafeBoxCoin(models.Model):
    _inherit = "safe.box.coin"

    type = fields.Selection(
        [("coin", "Coin"), ("note", "Note")], default="coin", required=True
    )
