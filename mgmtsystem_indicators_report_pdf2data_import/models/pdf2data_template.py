

from odoo import fields, models


class Pdf2dataTemplate(models.Model):

    _inherit = "pdf2data.template"

    mgmtsystem_indicator_template_id = fields.Many2one(
        "mgmtsystem.indicators.report.template"
    )
