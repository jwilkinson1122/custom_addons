

from odoo import fields, models


class PodiatryDiagnosticReportExpand(models.TransientModel):

    _inherit = "pod.diagnostic.report.expand"
    report_category_id = fields.Many2one(
        "pod.report.category",
        related="diagnostic_report_id.report_category_id",
    )
