# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Patient(models.Model):
    _inherit = "patient"

    partner_id = fields.Many2one(
        "res.partner", string="Doctor", index=True, tracking=True
    )
