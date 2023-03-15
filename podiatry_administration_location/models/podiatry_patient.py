
from odoo import fields, models


class PodiatryPatient(models.Model):
    _inherit = "podiatry.patient"

    podiatry_location_primary_id = fields.Many2one(
        string="Primary Practice",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
    podiatry_location_secondary_ids = fields.Many2many(
        string="Secondary Practice",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
