# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class ActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    def _get_pod_values(self, vals, parent=False, plan=False, action=False):
        res = super(ActivityDefinition, self)._get_pod_values(
            vals, parent, plan, action
        )
        request_models = self.env.ref(
            "pod_clinical_procedure.model_pod_procedure_request"
        )
        request_models |= self.env.ref(
            "pod_clinical_laboratory.model_pod_laboratory_request"
        )
        if self.model_id in request_models and action:
            res.update(
                {
                    "variable_fee": action.variable_fee,
                    "fixed_fee": action.fixed_fee,
                }
            )
        return res
