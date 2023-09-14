

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryRequest(models.AbstractModel):
    _inherit = "pod.request"

    encounter_id = fields.Many2one(
        comodel_name="pod.encounter", ondelete="restrict", index=True
    )

    @api.constrains("patient_id", "encounter_id")
    def _check_patient_encounter(self):
        if self.env.context.get("no_check_patient", False):
            return
        for record in self.filtered(lambda r: r.encounter_id):
            if record.encounter_id.patient_id != record.patient_id:
                raise ValidationError(
                    _("Inconsistency between patient and encounter")
                )

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.encounter_id)
        return res
