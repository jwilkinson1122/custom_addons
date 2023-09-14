# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import models


class PodiatryCareplanAddPlanDefinition(models.TransientModel):
    _inherit = "pod.careplan.add.plan.definition"

    def _get_values(self):
        values = super()._get_values()
        if self.careplan_id.encounter_id:
            values["encounter_id"] = self.careplan_id.encounter_id.id
        return values
