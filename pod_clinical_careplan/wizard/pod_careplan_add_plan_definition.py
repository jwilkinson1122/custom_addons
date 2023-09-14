# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryCareplanAddPlanDefinition(models.TransientModel):
    _name = "pod.careplan.add.plan.definition"
    _inherit = "pod.add.plan.definition"
    _description = "Add a plan Definition on a Careplan"

    patient_id = fields.Many2one(
        related="careplan_id.patient_id", readonly=True
    )

    careplan_id = fields.Many2one(
        comodel_name="pod.careplan", string="Care plan", required=True
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        required=True,
    )

    def _get_context(self):
        return {
            "origin_model": self.careplan_id._name,
            "origin_id": self.careplan_id.id,
        }

    def _get_values(self):
        values = super(PodiatryCareplanAddPlanDefinition, self)._get_values()
        values["careplan_id"] = self.careplan_id.id
        return values
