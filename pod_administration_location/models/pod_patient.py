# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryPatient(models.Model):
    _inherit = "pod.patient"

    pod_location_primary_id = fields.Many2one(
        string="Primary Podiatry Center",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
    pod_location_secondary_ids = fields.Many2many(
        string="Secondary Podiatry Centers",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
