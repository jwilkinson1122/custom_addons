

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryEncounterAddCareplan(models.TransientModel):
    _name = "pod.encounter.add.careplan"
    _description = "pod.encounter.add.careplan"

    @api.model
    def get_encounter_states(self):
        return ["arrived", "in-progress", "on-leave"]

    @api.model
    def get_careplan_states(self):
        return ["draft", "active"]

    @api.model
    def default_practice(self):
        if self._context.get("default_encounter_id", False):
            return (
                self.env["pod.encounter"]
                .browse(self._context.get("default_encounter_id", False))
                .practice_id
            )

    encounter_id = fields.Many2one(
        "pod.encounter",
        required=True,
        readonly=True,
        domain=[("state", "in", get_encounter_states)],
    )
    patient_id = fields.Many2one(
        "pod.patient", related="encounter_id.patient_id", readonly=True
    )
    practice_id = fields.Many2one(
        "res.partner",
        default=default_practice,
        required=True,
        domain=[("is_practice", "=", True)],
    )
    payor_id = fields.Many2one(
        "res.partner", required=True, domain="[('is_payor', '=', True)]"
    )
    sub_payor_id = fields.Many2one(
        "res.partner",
        domain="[('payor_id', '=', payor_id), ('is_sub_payor', '=', True)]",
    )
    coverage_id = fields.Many2one(
        "pod.coverage", domain="[('patient_id','=', patient_id)]"
    )
    coverage_template_id = fields.Many2one(
        "pod.coverage.template",
        required=True,
        domain="[('payor_id', '=', payor_id)]",
    )
    subscriber_magnetic_str = fields.Char()
    subscriber_id = fields.Char()

    def get_careplan_values(self):
        return {
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id,
            "practice_id": self.practice_id.id,
            "coverage_id": self.patient_id.get_coverage(
                template=self.coverage_template_id,
                coverage=self.coverage_id,
                subscriber_id=self.subscriber_id,
                magnetic_str=self.subscriber_magnetic_str,
            ).id,
            "sub_payor_id": self.sub_payor_id.id,
        }

    @api.onchange("payor_id")
    def onchange_payor(self):
        if self.payor_id:
            if self.coverage_template_id.payor_id != self.payor_id:
                self.coverage_template_id = False
            if self.sub_payor_id.payor_id != self.payor_id:
                self.sub_payor_id = False

    @api.onchange("coverage_template_id")
    def onchange_coverage_template(self):
        if self.coverage_template_id:
            if self.coverage_template_id != self.coverage_id.coverage_template_id:
                self.coverage_id = False
                self.subscriber_id = False
                self.subscriber_magnetic_str = False

    @api.onchange("coverage_id")
    def onchange_coverage(self):
        if self.coverage_id:
            self.payor_id = self.coverage_id.coverage_template_id.payor_id
            self.coverage_template_id = self.coverage_id.coverage_template_id
            self.subscriber_id = self.coverage_id.subscriber_id
            self.subscriber_magnetic_str = self.coverage_id.subscriber_magnetic_str

    def run(self):
        self.ensure_one()
        if self.encounter_id.state not in self.get_encounter_states():
            raise ValidationError(_("Encounter is not valid"))
        vals = self.get_careplan_values()
        cp = self.encounter_id.careplan_ids.filtered(
            lambda r: (
                r.coverage_id.id == vals.get("coverage_id", False)
                and (
                    (
                        r.sub_payor_id
                        and r.sub_payor_id.id == vals.get("sub_payor_id", False)
                    )
                    or (not r.sub_payor_id and not vals.get("sub_payor_id", False))
                )
                and r.fhir_state in self.get_careplan_states()
            )
        )
        if cp:
            return cp[0]
        return self.env["pod.careplan"].create(vals)
