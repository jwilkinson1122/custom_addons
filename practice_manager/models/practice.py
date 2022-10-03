# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Practice(models.Model):
    _inherit = "practice"

    partner_id = fields.Many2one(
        "res.partner", string="Manager", index=True, tracking=True
    )
