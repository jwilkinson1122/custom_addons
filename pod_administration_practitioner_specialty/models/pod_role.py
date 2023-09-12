from odoo import fields, models

# FHIR Entity: PractitionerRole
# (https://www.hl7.org/fhir/practitionerrole.html)

class PodiatryRole(models.Model):
    _inherit = "pod.role"

    specialty_required = fields.Boolean(default=False)
