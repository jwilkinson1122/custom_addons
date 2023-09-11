from odoo import api, fields, models


class PodiatrySCTConcept(models.Model):
    _inherit = "pod.sct.concept"

    is_clinical_finding = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_finding"
    )
    is_clinical_substance = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_substance"
    )
    is_podiatric_product = fields.Boolean(
        store=True, index=True, compute="_compute_is_podiatric_product"
    )

    @api.depends("parent_ids")
    def _compute_is_clinical_finding(self):
        for record in self:
            record.is_clinical_finding = record.check_property(
                "is_clinical_finding", ["404684003"]
            )

    @api.depends("parent_ids")
    def _compute_is_clinical_substance(self):
        for record in self:
            record.is_clinical_substance = record.check_property(
                "is_clinical_substance", ["105590001"]
            )

    @api.depends("parent_ids")
    def _compute_is_podiatric_product(self):
        for record in self:
            record.is_podiatric_product = record.check_property(
                "is_podiatric_product", ["373873005"]
            )
