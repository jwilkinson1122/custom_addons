# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ActivityDefinition(models.Model):
    # FHIR entity: Activity Definition
    # (https://www.hl7.org/fhir/activitydefinition.html)
    _inherit = "workflow.activity.definition"

    def _get_pod_models(self):
        return super()._get_pod_models() + ["pod.device.request"]

    def _get_pod_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )
        if self.model_id.model == "pod.device.request":
            values.update(
                {
                    "product_id": self.service_id.id,
                    "product_uom_id": self.service_id.uom_id.id,
                }
            )
        return values
