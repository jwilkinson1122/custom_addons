

from odoo import _, api, models
from odoo.exceptions import ValidationError


class PodiatryEncounter(models.Model):

    _inherit = "pod.encounter"

    @api.model
    def create_encounter(
        self, patient=False, patient_vals=False, practice=False, **kwargs
    ):
        encounter = self._create_encounter(
            patient=patient,
            patient_vals=patient_vals,
            practice=practice,
            **kwargs,
        )
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_administration_encounter.pod_encounter_action"
        )
        result["views"] = [(False, "form")]
        result["res_id"] = encounter.id
        return result

    @api.model
    def _create_encounter(
        self, patient=False, patient_vals=False, practice=False, **kwargs
    ):
        if not patient_vals and not patient:
            raise ValidationError(_("Patient information is required"))
        if not practice:
            raise ValidationError(_("Practice is required"))
        if not patient_vals:
            patient_vals = {}
        if not patient:
            patient = self.env["pod.patient"].create(patient_vals)
        else:
            if isinstance(patient, int):
                patient = self.env["pod.patient"].browse(patient)
            new_patient_vals = {}
            for field in patient_vals:
                if field not in patient._fields:
                    continue
                original_patient_value = patient[field]
                if isinstance(original_patient_value, models.Model):
                    original_patient_value = original_patient_value.id
                if patient_vals[field] != original_patient_value:
                    new_patient_vals[field] = patient_vals[field]
            if new_patient_vals:
                patient.write(new_patient_vals)
                patient.flush()
        if isinstance(practice, int):
            practice = self.env["res.partner"].browse(practice)
        return self.create(self._create_encounter_vals(patient, practice, **kwargs))

    def _create_encounter_vals(self, patient, practice, **kwargs):
        return {"patient_id": patient.id, "practice_id": practice.id}
