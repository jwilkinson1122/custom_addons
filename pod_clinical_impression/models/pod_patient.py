

from odoo import _, api, fields, models


class PodiatryPatient(models.Model):

    _inherit = "pod.patient"

    pod_impression_ids = fields.One2many(
        "pod.clinical.impression",
        inverse_name="patient_id",
    )
    impression_specialty_ids = fields.Many2many(
        "pod.specialty", compute="_compute_impression_specialties"
    )

    family_history_ids = fields.One2many(
        "pod.family.member.history", inverse_name="patient_id"
    )

    family_history_count = fields.Integer(
        compute="_compute_family_history_count"
    )

    condition_ids = fields.One2many(
        comodel_name="pod.condition",
        string="Conditions Warning",
        related="pod_impression_ids.condition_ids",
    )

    condition_count = fields.Integer(
        related="pod_impression_ids.condition_count"
    )

    @api.depends("family_history_ids")
    def _compute_family_history_count(self):
        self.family_history_count = len(self.family_history_ids)

    @api.depends("pod_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = (
                record.pod_impression_ids.mapped("specialty_id")
            )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        encounter = self._get_last_encounter()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_clinical_impression."
            "pod_clinical_impression_act_window"
        )
        action["domain"] = [("patient_id", "=", self.id)]
        if encounter:
            action["context"] = {
                "default_encounter_id": encounter.id,
                "search_default_filter_not_cancelled": True,
            }
        return action

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "pod_clinical_impression."
            "pod_family_member_history_action"
        )
        action["domain"] = [
            ("patient_id", "=", self.id),
        ]

        action["context"] = {"default_patient_id": self.id}
        return action

    def create_family_member_history(self):
        self.ensure_one()
        view_id = self.env.ref(
            "pod_clinical_impression.pod_family_member_history_view_form"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "pod.family.member.history",
            "name": _("Create family member history"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }
