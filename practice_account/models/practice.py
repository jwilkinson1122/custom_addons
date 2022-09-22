

from odoo import fields, models


class Practice(models.Model):
    _inherit = "practice"

    partner_id = fields.Many2one(
        "res.partner", string="Account", index=True, tracking=True
    )
