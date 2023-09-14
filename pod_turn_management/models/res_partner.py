

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    turn_specialty_ids = fields.Many2many(
        "pod.turn.specialty", string="Turn Specialties", readonly=True
    )
