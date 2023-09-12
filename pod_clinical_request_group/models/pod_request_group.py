from odoo import fields, models


# FHIR Rntity: Request Group (https://www.hl7.org/fhir/requestgroup.html)

class RequestGroup(models.Model):
    _name = "pod.request.group"
    _description = "Request Group"
    _inherit = "pod.request"

    request_group_ids = fields.One2many(inverse_name="request_group_id")

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("pod.request.group")
            or "/"
        )

    def _get_parent_field_name(self):
        return "request_group_id"

    def action_view_request_parameters(self):
        return {
            "view": "pod_clinical_request_group."
            "pod_request_group_window_action",
            "view_form": "pod.request.group.form",
        }
