

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_values(self, vals, parent=False, plan=False, action=False):
        res = super()._get_pod_values(vals, parent, plan, action)
        if parent:
            res.update({"sub_payor_id": parent.sub_payor_id.id or False})
        if self.model_id.model == "pod.device.request":
            # Device requests should have quantity equal to 1
            res["qty"] = 1
        return res

    def _find_relation_activity(self, vals, parent, plan, action):
        res = super()._find_relation_activity(vals, parent, plan, action)
        return res
