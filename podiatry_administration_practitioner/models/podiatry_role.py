

from odoo import fields, models


class PodiatryRole(models.Model):
    # : PractitionerRole/code
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _name = "podiatry.role"
    _description = "Practitioner Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
