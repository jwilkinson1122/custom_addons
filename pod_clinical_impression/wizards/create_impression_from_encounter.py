

from datetime import datetime, timedelta

from odoo import api, fields, models


class CreateImpressionFromEncounter(models.TransientModel):

    _name = "create.impression.from.encounter"
    _description = "Create Impression From Encounter"

    patient_id = fields.Many2one(
        "pod.patient", required=True, related="encounter_id.patient_id"
    )
    # The field patient_id is used for the domain of the encounter_id.
    # This way, even if coming from the view encounter, the default encounter
    # is the current but can be changed.

    specialty_id = fields.Many2one("pod.specialty", required=True)
    encounter_id = fields.Many2one(
        "pod.encounter",
        required=True,
    )
    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. REVISE THE CODE",
        readonly=True,
    )

    def _get_impression_vals(self):
        return {
            "default_encounter_id": self.encounter_id.id,
            "default_specialty_id": self.specialty_id.id,
        }

    def generate(self):
        self.ensure_one()
        action = self.env["pod.clinical.impression"].get_formview_action()
        action["context"] = self._get_impression_vals()
        return action

    @api.onchange("encounter_id")
    def _onchange_encounter_date(self):
        if datetime.now() - self.encounter_id.create_date >= timedelta(days=7):
            self.show_encounter_warning = True
