

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_podiatry_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_podiatry_values(
            vals, parent, plan, action
        )

        if parent and parent._name == "podiatry.request.group":
            values["request_group_id"] = parent.id
        return values
