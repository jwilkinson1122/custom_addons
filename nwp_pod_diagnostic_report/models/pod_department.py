

from odoo import fields, models


class PodiatryDepartment(models.Model):

    _name = "pod.department"
    _inherit = "pod.abstract"
    _description = "Podiatry Department"

    name = fields.Char(required=True)
    with_department_report_header = fields.Boolean(default=True)
    diagnostic_report_header = fields.Html(translate=True, sanitize=False)
    report_category_ids = fields.One2many(
        comodel_name="pod.report.category",
        inverse_name="pod_department_id",
    )
    user_ids = fields.Many2many("res.users")
    without_practitioner = fields.Boolean(
        help="When marked, the practitioner "
        "will not appear in the report when validated"
    )

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].sudo().next_by_code("pod.department") or "/"
