
from odoo import api, fields, models


class PodPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _inherit = "pod.patient"

    coverage_ids = fields.One2many(
        string="Coverage",
        comodel_name="pod.coverage",
        inverse_name="patient_id",
    )
    coverage_count = fields.Integer(
        compute="_compute_coverage_count",
        string="# of Coverages",
        copy=False,
        default=0,
    )

    @api.depends("coverage_ids")
    def _compute_coverage_count(self):
        for record in self:
            record.coverage_count = len(record.coverage_ids)

    def action_view_coverage(self):
        action = self.env.ref(
            "pod_financial_coverage.pod_coverage_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.coverage_ids) == 1:
            res = self.env.ref("pod.coverage.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.coverage_ids.id
        return result
