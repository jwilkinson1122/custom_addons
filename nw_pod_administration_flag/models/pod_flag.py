from odoo import fields, models

# FHIR Entity: Flag (https://www.hl7.org/fhir/flag.html)

class PodiatryFlag(models.Model):
    _inherit = "pod.flag"

    flag = fields.Char(related="category_id.flag", readonly=True)
    level = fields.Selection(related="category_id.level", readonly=True)
