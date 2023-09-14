

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    practitioner_condition_ids = fields.One2many(
        "pod.practitioner.condition",
        inverse_name="practitioner_id",
        copy=False,
    )
