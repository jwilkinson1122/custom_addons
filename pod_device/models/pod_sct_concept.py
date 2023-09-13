from odoo import api, fields, models


class PodiatrySCTConcept(models.Model):
    _inherit = "pod.sct.concept"

    is_device_form = fields.Boolean(
        store=True, index=True, compute="_compute_is_device_form"
    )

    is_device_code = fields.Boolean(
        store=True, index=True, compute="_compute_is_device_code"
    )

    @api.depends("parent_ids")
    def _compute_is_device_form(self):
        for record in self:
            record.is_device_form = record.check_property(
                "is_device_form", ["421967003"]
            )

    @api.depends("parent_ids")
    def _compute_is_device_code(self):
        for record in self:
            record.is_device_code = record.check_property(
                "is_device_code", ["373873005", "106181007", "410942007"]
            )
