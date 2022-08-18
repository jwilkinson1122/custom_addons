

from odoo import fields, models


class PodCarePlan(models.Model):

    _name = "pod.careplan"
    _description = "Podiatry Care Plan"
    _inherit = "pod.request"

    internal_identifier = fields.Char(string="Careplan")
    start_date = fields.Datetime(string="start date")
    end_date = fields.Datetime(string="End date")
    careplan_ids = fields.One2many(inverse_name="careplan_id")

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.careplan") or "/"

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
