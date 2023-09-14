

from odoo import api, fields, models


class PodiatryPatient(models.Model):
    _inherit = "pod.patient"

    request_group_ids = fields.One2many(
        "pod.request.group", inverse_name="patient_id"
    )
    last_coverage_id = fields.Many2one(
        "pod.coverage", compute="_compute_last_coverage"
    )

    @api.depends("request_group_ids")
    def _compute_last_coverage(self):
        for rec in self:
            requests = rec.request_group_ids.filtered(lambda r: r.coverage_id).sorted(
                "id", reverse=True
            )
            if requests:
                rec.last_coverage_id = requests[0].coverage_id
            else:
                rec.last_coverage_id = False
