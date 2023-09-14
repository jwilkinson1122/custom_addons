# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PodiatryLaboratoryEvent(models.Model):
    # FHIR Entity: Procedure (https://www.hl7.org/fhir/procedure.html)
    _name = "pod.laboratory.event"
    _description = "Podiatry Laboratory Event"
    _inherit = "pod.event"

    internal_identifier = fields.Char(string="Laboratory Event")
    laboratory_request_id = fields.Many2one(
        comodel_name="pod.laboratory.request",
        string="Laboratory request",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: BasedOn

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.laboratory.event") or "/"

    @api.constrains("laboratory_request_id", "patient_id")
    def _check_patient_device(self):
        if not self.env.context.get("no_check_patient", False):
            if self.patient_id != self.laboratory_request_id.patient_id:
                raise ValidationError(_("Patient inconsistency"))
