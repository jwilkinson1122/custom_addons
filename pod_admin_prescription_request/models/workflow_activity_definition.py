

from odoo import models


class ActivityDefinition(models.Model):
    #  entity: Activity Definition
    # (https://www.hl7.org/fhir/activitydefinition.html)
    _inherit = "workflow.activity.definition"

    def _get_podiatry_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_podiatry_values(
            vals, parent, plan, action
        )
        if self.model_id.model == "podiatry.device.request":
            values.update(
                {
                    "product_id": self.service_id.id,
                    "product_uom_id": self.service_id.uom_id.id,
                }
            )
        return values
