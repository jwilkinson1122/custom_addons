from odoo import api, models


class PodiatryEncounterAddCareplan(models.TransientModel):
    _inherit = "pod.encounter.add.careplan"

    @api.model
    def get_encounter_states(self):
        res = super().get_encounter_states()
        if self.env.context.get("on_validation", False):
            res.append("finished")
        return res
