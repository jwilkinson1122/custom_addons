from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class PodiatryRequestGroup(models.Model):
    _name = "pod.request.group"
    _inherit = ["pod.request.group", "pod.request"]

    can_change_plan = fields.Boolean(compute="_compute_can_change_plan")
    child_model = fields.Char()
    child_id = fields.Integer()

    @api.depends("state")
    def _compute_can_change_plan(self):
        for record in self:
            record.can_change_plan = record.state not in [
                "cancelled",
                "completed",
            ]

    def _get_authorization_context(self):
        return {
            "default_request_group_id": self.id,
            "default_authorization_number": self.authorization_number,
            "default_authorization_method_id": (
                self.authorization_method_id.id
                or self.coverage_agreement_item_id.authorization_method_id.id
            ),
        }

    def check_authorization_action(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_financial_coverage_request."
            "pod_request_group_check_authorization_action"
        )
        ctx = safe_eval(result["context"]) or {}
        ctx.update(self._get_authorization_context())
        result["context"] = ctx
        return result

    @api.model
    def _pass_performer(self, activity, parent, plan, action):
        return True
