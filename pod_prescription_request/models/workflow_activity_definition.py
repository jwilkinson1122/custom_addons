from odoo import models

# FHIR entity: Activity Definition
# (https://www.hl7.org/fhir/activitydefinition.html)
    
class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_models(self):
        return super()._get_pod_models() + ["pod.prescription.request"]

    def _get_pod_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )
        if self.model_id.model == "pod.prescription.request":
            values.update(
                {
                    "product_id": self.service_id.id,
                    "product_uom_id": self.service_id.uom_id.id,
                }
            )
        return values
