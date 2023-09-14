

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_values(self, vals, parent=False, plan=False, action=False):
        res = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )
        if action:
            res.update({"is_blocking": action.is_blocking})
        return res
