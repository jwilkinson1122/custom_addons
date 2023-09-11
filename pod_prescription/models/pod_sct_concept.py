from odoo import api, fields, models


class PodiatrySCTConcept(models.Model):
    _inherit = "pod.sct.concept"

    is_prescription_form = fields.Boolean(
        store=True, index=True, compute="_compute_is_prescription_form"
    )

    is_prescription_code = fields.Boolean(
        store=True, index=True, compute="_compute_is_prescription_code"
    )

    @api.depends("parent_ids")
    def _compute_is_prescription_form(self):
        for record in self:
            record.is_prescription_form = record.check_property(
                "is_prescription_form", ["421967003"]
            )

    @api.depends("parent_ids")
    def _compute_is_prescription_code(self):
        for record in self:
            record.is_prescription_code = record.check_property(
                "is_prescription_code", ["373873005", "106181007", "410942007"]
            )
