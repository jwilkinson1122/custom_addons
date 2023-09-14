

from odoo import fields, models


class PodiatryRole(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "pod.role"

    specialty_required = fields.Boolean(default=False)
