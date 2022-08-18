

from odoo import fields, models


class PodCareplanAddPlanDefinition(models.TransientModel):
    _name = "pod.careplan.add.plan.definition"
    _inherit = "pod.add.plan.definition"
    _description = "Add a plan Definition on a Careplan"

    def _domain_plan_definition(self):
        return [
            (
                "type_id",
                "=",
                self.env.ref("pod_workflow.pod_workflow").id,
            )
        ]

    patient_id = fields.Many2one(
        related="careplan_id.patient_id", readonly=True
    )

    careplan_id = fields.Many2one(
        comodel_name="pod.careplan", string="Care plan", required=True
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        domain=_domain_plan_definition,
        required=True,
    )

    def _get_context(self):
        return {
            "origin_model": self.careplan_id._name,
            "origin_id": self.careplan_id.id,
        }

    def _get_values(self):
        values = super(PodCareplanAddPlanDefinition, self)._get_values()
        values["careplan_id"] = self.careplan_id.id
        return values
