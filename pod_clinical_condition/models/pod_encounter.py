# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryEncounter(models.Model):
    _inherit = "pod.encounter"

    pod_condition_ids = fields.One2many(
        related="patient_id.pod_condition_ids",
    )
    pod_condition_count = fields.Integer(
        related="patient_id.pod_condition_count",
        string="# of Conditions",
    )
    pod_allergy_ids = fields.One2many(
        related="patient_id.pod_allergy_ids",
        domain=[("is_allergy", "=", True)],
    )
    pod_allergies_count = fields.Integer(
        related="patient_id.pod_allergies_count",
        string="# of Allergies",
    )

    pod_warning_ids = fields.One2many(
        related="patient_id.pod_warning_ids"
    )

    pod_warning_count = fields.Integer(
        related="patient_id.pod_warning_count",
        string="# of Warnings",
    )

    def action_view_pod_conditions(self):
        self.ensure_one()
        return self.patient_id.action_view_pod_conditions()

    def action_view_pod_warnings(self):
        self.ensure_one()
        return self.patient_id.action_view_pod_conditions()

    def action_view_pod_allergies(self):
        self.ensure_one()
        return self.patient_id.action_view_pod_allergies()

    def create_pod_clinical_condition(self):
        self.ensure_one()
        return self.patient_id.create_pod_clinical_condition()

    def create_allergy(self):
        self.ensure_one()
        return self.patient_id.create_allergy()
