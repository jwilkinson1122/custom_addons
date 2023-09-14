

from odoo import api, fields, models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    requires_document_template = fields.Boolean(
        compute="_compute_requires_document_template"
    )
    document_type_id = fields.Many2one(
        "pod.document.type",
        domain=[("state", "=", "current")],
        ondelete="restrict",
    )

    @api.depends("model_id")
    def _compute_requires_document_template(self):
        for record in self:
            record.requires_document_template = bool(
                record.model_id.model == "pod.document.reference"
            )

    def _get_pod_models(self):
        return super()._get_pod_models() + ["pod.document.reference"]

    @api.onchange("model_id")
    def _onchange_model(self):
        if self.model_id.model != "pod.document.reference":
            self.document_type_id = False

    def _get_pod_values(self, vals, parent=False, plan=False, action=False):
        values = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )
        if self.model_id.model == "pod.document.reference":
            values["document_type_id"] = self.document_type_id.id
        return values
