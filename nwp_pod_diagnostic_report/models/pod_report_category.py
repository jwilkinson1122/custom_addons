

from odoo import fields, models


class PodiatryReportCategory(models.Model):

    _name = "pod.report.category"
    _inherit = "pod.abstract"
    _description = "Podiatry Report Category"
    _order = "sequence"

    name = fields.Char(required=True)
    pod_department_id = fields.Many2one("pod.department")
    sequence = fields.Integer(default=20)

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("pod.report.category") or "/"
