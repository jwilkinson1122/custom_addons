

from odoo import api, fields, models


class PodiatryEncounter(models.Model):

    _inherit = "pod.encounter"

    external_request_ids = fields.One2many(
        comodel_name="pod.procedure.external.request",
        inverse_name="encounter_id",
    )

    external_request_count = fields.Integer(
        compute="_compute_external_request_count"
    )

    @api.depends("external_request_ids")
    def _compute_external_request_count(self):
        for record in self:
            record.external_request_count = len(
                record.external_request_ids.filtered(
                    lambda r: r.state != "cancelled"
                )
            )

    def action_view_external_request(self):
        self.ensure_one()
        action = self.env.ref(
            "pod_procedure_external.pod_procedure_external_request_act_window"
        ).read()[0]
        action["domain"] = [("encounter_id", "=", self.id)]
        action["context"] = {"search_default_filter_not_cancelled": True}
        return action
