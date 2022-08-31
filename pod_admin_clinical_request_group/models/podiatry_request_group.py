

from odoo import fields, models


class RequestGroup(models.Model):
    #  Rntity: Request Group (https://www.hl7.org/fhir/requestgroup.html)
    _name = "podiatry.request.group"
    _description = "Request Group"
    _inherit = "podiatry.request"

    request_group_ids = fields.One2many(inverse_name="request_group_id")
    internal_identifier = fields.Char(string="Request group")

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("podiatry.request.group")
            or "Req"
        )

    def _get_parent_field_name(self):
        return "request_group_id"

    def action_view_request_parameters(self):
        return {
            "view": "podiatry_clinical_request_group."
            "podiatry_request_group_window_action",
            "view_form": "podiatry.request.group.form",
        }
