
from odoo import api, fields, models


class PodSCTConcept(models.Model):
    _inherit = "pod.sct.concept"

    is_prescription_form = fields.Boolean(
        store=True, index=True, compute="_compute_is_prescription_form"
    )

    is_medical_device_code = fields.Boolean(
        store=True, index=True, compute="_compute_is_medical_device_code"
    )

    @api.depends("parent_ids")
    def _compute_is_prescription_form(self):
        for record in self:
            record.is_prescription_form = record.check_property(
                "is_prescription_form", ["421967003"]
            )

    @api.depends("parent_ids")
    def _compute_is_medical_device_code(self):
        for record in self:
            record.is_medical_device_code = record.check_property(
                "is_medical_device_code", [
                    "373873005", "106181007", "410942007"]
            )
