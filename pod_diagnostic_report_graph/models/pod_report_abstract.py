# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PodiatryReportAbstract(models.AbstractModel):

    _inherit = "pod.report.abstract"

    compute_graph = fields.Boolean()
    compute_html = fields.Boolean()

    hide_observations = fields.Boolean(help="Hide observations on report")
