# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryCarePlan(models.Model):
    # FHIR Entity: Care Plan
    # (https://www.hl7.org/fhir/careplan.html)
    _name = "pod.careplan"
    _description = "Podiatry Care Plan"
    _inherit = "pod.request"

    internal_identifier = fields.Char()
    start_date = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: Period
    end_date = fields.Datetime(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: Period

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("pod.careplan")
            or "/"
        )

    def draft2active_values(self):
        res = super().draft2active_values()
        res["start_date"] = fields.Datetime.now()
        return res

    def active2completed_values(self):
        res = super().active2completed_values()
        res["end_date"] = fields.Datetime.now()
        return res

    def _get_parent_field_name(self):
        return "careplan_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_clinical_careplan.pod_careplan_action",
            "view_form": "pod.careplan.view.form",
        }
