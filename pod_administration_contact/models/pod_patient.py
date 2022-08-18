
from odoo import api, fields, models


class PodPatient(models.Model):

    _inherit = "pod.patient"

    contact_ids = fields.One2many(
        comodel_name="pod.contact", inverse_name="patient_id"
    )
    contact_count = fields.Integer(compute="_compute_contact_count")

    @api.depends("contact_ids")
    def _compute_contact_count(self):
        for record in self:
            record.contact_count = len(record.contact_ids)

    def action_view_contact_ids(self):
        self.ensure_one()
        action = self.env.ref(
            "pod_administration_contact.pod_contact_action"
        ).read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        return action
