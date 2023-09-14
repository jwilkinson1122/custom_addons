# Copyright 2021 n
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PodiatryCareplanAddPlanDefinition(models.TransientModel):

    _inherit = "pod.careplan.add.plan.definition"

    def _run(self):
        company = self.product_id.product_tmpl_id.pod_center_company_ids.filtered(
            lambda r: r.center_id == self.center_id
        ).company_id
        if (
            company
            and self.careplan_id.encounter_id
            and not self.careplan_id.encounter_id.company_id
        ):
            self.careplan_id.encounter_id.write({"company_id": company.id})
        return super(PodiatryCareplanAddPlanDefinition, self)._run()
