

from odoo import models


class PodCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "pod.careplan.add.plan.definition"

    def _get_values(self):
        values = super()._get_values()
        if self.careplan_id.contact_id:
            values["contact_id"] = self.careplan_id.contact_id.id
        return values
