
from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )

        if parent and parent._name == "pod.request.group":
            values["request_group_id"] = parent.id
        return values
