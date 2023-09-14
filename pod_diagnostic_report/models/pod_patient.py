# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class PodiatryPatient(models.Model):

    _inherit = "pod.patient"

    diagnostic_report_ids = fields.One2many(
        "pod.diagnostic.report",
        inverse_name="patient_id",
        domain=[("fhir_state", "!=", "cancelled")],
    )

    def action_view_observations_with_concept(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_diagnostic_report."
            "pod_diagnostic_report_concepts_patient_act_window"
        )
        action["domain"] = [
            ("patient_id", "=", self.id),
            ("concept_id", "!=", False),
            ("state", "=", "final"),
        ]
        return action
