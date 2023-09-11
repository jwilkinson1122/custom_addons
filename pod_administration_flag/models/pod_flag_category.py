from odoo import fields, models

# FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)

class PodiatryFlag(models.Model):
    _name = "pod.flag.category"
    _description = "Podiatry Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
