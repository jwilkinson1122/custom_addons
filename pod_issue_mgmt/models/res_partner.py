

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    quality_issue_ids = fields.One2many(
        "mgmtsystem.quality.issue",
        inverse_name="partner_id",
    )
    quality_issue_count = fields.Integer(compute="_compute_quality_issue_count")

    @api.depends("quality_issue_ids")
    def _compute_quality_issue_count(self):
        for record in self:
            record.quality_issue_count = len(record.quality_issue_ids)

    def action_view_quality_issues(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_issue_mgmt.mgmtsystem_quality_issue_act_window"
        )
        if len(self.quality_issue_ids) > 1:
            action["domain"] = [("partner_id", "=", self.id)]
        elif self.quality_issue_ids:
            action["views"] = [
                (
                    self.env.ref(
                        "pod_issue_mgmt.mgmtsystem_quality_issue_form_view"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = self.quality_issue_ids.id
        return action
