

from odoo import fields, models


class ResPartner(models.Model):
    # : PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "res.partner"

    specialty_ids = fields.Many2many(
        "podiatry.specialty", string="Specialties")
