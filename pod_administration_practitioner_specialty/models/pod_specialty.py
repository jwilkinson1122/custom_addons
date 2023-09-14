# Copyright 2017 LasLabs Inc.


from odoo import fields, models


class PodiatrySpecialty(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _name = "pod.specialty"
    _description = "Specialty"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sct_code = fields.Many2one(
        comodel_name="pod.sct.concept",
        domain=[("is_specialty", "=", True)],
    )  # FHIR Field: code
