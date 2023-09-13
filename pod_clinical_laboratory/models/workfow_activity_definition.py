

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_models(self):
        return super()._get_pod_models() + ["pod.laboratory.request"]
