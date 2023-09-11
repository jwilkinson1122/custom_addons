from odoo import fields, models

# FHIR Entity: PractitionerRole
# (https://www.hl7.org/fhir/practitionerrole.html)
    
class ResPartner(models.Model):
    _inherit = "res.partner"

    specialty_ids = fields.Many2many("pod.specialty", string="Specialties")
