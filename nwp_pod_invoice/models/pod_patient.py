from odoo import fields, models


class PodiatryPatient(models.Model):
    _inherit = "pod.patient"

    related_partner_ids = fields.Many2many(
        "res.partner",
        "pod_patient_invoicable_partner",
        "patient_id",
        "partner_id",
    )
