from odoo import fields, models


class PodiatryCoverageTemplate(models.Model):
    _inherit = "pod.coverage.template"

    laboratory_code = fields.Char(tracking=True)
