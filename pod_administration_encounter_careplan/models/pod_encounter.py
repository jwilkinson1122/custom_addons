from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryEncounter(models.Model):
    _inherit = "pod.encounter"

    careplan_ids = fields.One2many(
        comodel_name="pod.careplan", inverse_name="encounter_id"
    )
    careplan_count = fields.Integer(compute="_compute_careplan_count")

    @api.depends("careplan_ids")
    def _compute_careplan_count(self):
        for record in self:
            record.careplan_count = len(record.careplan_ids)

    def action_view_careplans(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_clinical_careplan.pod_careplan_action"
        )
        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_encounter_id": self.id,
        }
        result["domain"] = "[('encounter_id', '=', " + str(self.id) + ")]"
        if len(self.careplan_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.careplan_ids.id
        return result

    @api.constrains("patient_id")
    def _check_patient(self):
        if not self.env.context.get("no_check_patient", False):
            for rec in self:
                if rec.careplan_ids.filtered(
                    lambda r: r.patient_id != rec.patient_id
                ):
                    raise ValidationError(_("Patient must be consistent"))
