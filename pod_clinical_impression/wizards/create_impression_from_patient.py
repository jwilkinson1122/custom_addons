# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class CreateImpressionFromPatient(models.TransientModel):

    _name = "create.impression.from.patient"
    _description = "Create Impression From Patient"

    patient_id = fields.Many2one("pod.patient", required=True)

    specialty_id = fields.Many2one("pod.specialty", required=True)
    encounter_id = fields.Many2one(
        "pod.encounter",
        required=True,
        compute="_compute_default_encounter",
    )
    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. REVIEW THE CODE",
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

    @api.onchange("patient_id")
    def _compute_default_encounter(self):
        self.encounter_id = self.patient_id._get_last_encounter()

    @api.onchange("encounter_id")
    def _onchange_encounter_date(self):
        if datetime.now() - self.encounter_id.create_date >= timedelta(days=7):
            self.show_encounter_warning = True
