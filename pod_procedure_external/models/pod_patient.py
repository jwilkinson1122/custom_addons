
from odoo import fields, models


class PodiatryPatient(models.Model):

    _inherit = "pod.patient"

    external_procedure_ids = fields.One2many(
        "pod.procedure.external.request",
        inverse_name="patient_id",
        domain=[("fhir_state", "!=", "cancelled")],
    )
