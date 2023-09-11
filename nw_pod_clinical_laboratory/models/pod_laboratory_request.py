from odoo import api, fields, models


class PodiatryLaboratoryRequest(models.Model):
    _inherit = "pod.laboratory.request"

    laboratory_service_ids = fields.Many2many(
        "pod.laboratory.service", readonly=True
    )
    laboratory_event_ids = fields.One2many(
        string="Laboratory Events",
        states={
            "draft": [("readonly", False)],
            "active": [("readonly", False)],
        },
    )
    event_coverage_agreement_id = fields.Many2one(
        "pod.coverage.agreement",
        compute="_compute_event_coverage_agreement_id",
    )

    @api.depends("service_id", "coverage_id.coverage_template_id", "center_id")
    def _compute_event_coverage_agreement_id(self):
        for record in self:
            cai = self.env["pod.coverage.agreement.item"].get_item(
                record.service_id,
                record.coverage_id.coverage_template_id,
                record.center_id,
            )
            agreement = self.env["pod.coverage.agreement"]
            if cai:
                agreement = cai.coverage_agreement_id
            record.event_coverage_agreement_id = agreement
