from odoo import fields, models


class PrescriptionsFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _name = "prescriptions.flag.category"
    _description = "Prescriptions Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
