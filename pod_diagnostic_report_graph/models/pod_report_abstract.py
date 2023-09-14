

from odoo import fields, models


class PodiatryReportAbstract(models.AbstractModel):

    _inherit = "pod.report.abstract"

    compute_graph = fields.Boolean()
    compute_html = fields.Boolean()

    hide_observations = fields.Boolean(help="Hide observations on report")
