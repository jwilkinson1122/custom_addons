from odoo import fields, models

# FHIR Entity: PractitionerRole/code
# (https://www.hl7.org/fhir/practitionerrole.html)

class PodiatryRole(models.Model):
    _name = "pod.role"
    _description = "Practitioner Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
