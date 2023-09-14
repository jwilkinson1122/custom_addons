# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PodiatryReportAbstract(models.AbstractModel):

    _inherit = "pod.report.abstract"

    report_category_id = fields.Many2one("pod.report.category")
    pod_department_id = fields.Many2one(
        "pod.department",
        related="report_category_id.pod_department_id",
        store=True,
    )
    pod_department_header = fields.Html()
