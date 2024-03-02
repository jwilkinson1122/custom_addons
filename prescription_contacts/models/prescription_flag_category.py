from odoo import fields, models


class PrescriptionFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _name = "prescription.flag.category"
    _description = "Prescription Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
