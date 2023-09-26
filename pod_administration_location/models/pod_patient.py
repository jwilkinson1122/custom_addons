from odoo import fields, models


class PodiatryPatient(models.Model):
    _inherit = "pod.patient"

    pod_location_primary_id = fields.Many2one(
        string="Primary Podiatry Practice",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
    pod_location_secondary_ids = fields.Many2many(
        string="Secondary Podiatry Practices",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
