

from odoo import fields, models


class PodiatrySpecialty(models.Model):
    # : PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _name = "podiatry.specialty"
    _description = "Specialty"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sct_code = fields.Many2one(
        comodel_name="podiatry.sct.concept",
        domain=[("is_specialty", "=", True)],
    )  # Field: code
