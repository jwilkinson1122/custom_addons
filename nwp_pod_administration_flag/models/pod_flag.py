from odoo import fields, models


class PodiatryFlag(models.Model):
    # FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)
    _inherit = "pod.flag"

    flag = fields.Char(related="category_id.flag", readonly=True)
    level = fields.Selection(related="category_id.level", readonly=True)
