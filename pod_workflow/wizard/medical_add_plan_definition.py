# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MedicalAddPlanDefinition(models.TransientModel):
    _name = "medical.add.plan.definition"
    _description = "Add plan definition"

    patient_id = fields.Many2one(
        comodel_name="medical.patient", string="Patient", required=True
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        required=True,
    )

    def _get_values(self):
        return {
            "patient_id": self.patient_id.id,
            "name": self.plan_definition_id.name,
        }

    def _get_context(self):
        return {
            "origin_model": self.patient_id._name,
            "origin_id": self.patient_id.id,
        }

    def _run(self):
        self.ensure_one()
        vals = self._get_values()
        ctx = self._get_context()
        ctx.update(self.env.context)
        return self.plan_definition_id.with_context(
            ctx
        ).execute_plan_definition(vals)

    def run(self):
        res = self._run()
        if not res:
            raise UserError(_("No requests were created"))
