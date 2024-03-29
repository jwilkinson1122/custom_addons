from odoo import fields, models


class PodiatryFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _name = "pod.flag.category"
    _description = "Podiatry Category Flag"

    name = fields.Char(required=True)
    description = fields.Text()
    active = fields.Boolean(required=True, default=True)
