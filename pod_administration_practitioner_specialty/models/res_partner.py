# Copyright 2017 LasLabs Inc.


from odoo import fields, models


class ResPartner(models.Model):
    # FHIR Entity: PractitionerRole
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _inherit = "res.partner"

    specialty_ids = fields.Many2many("pod.specialty", string="Specialties")
