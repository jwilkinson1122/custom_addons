# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryCoverageTemplate(models.Model):
    _inherit = "pod.coverage.template"

    agreement_ids = fields.Many2many(
        string="Coverage Templates",
        comodel_name="pod.coverage.agreement",
        relation="pod_coverage_agreement_pod_coverage_template_rel",
        column1="coverage_template_id",
        column2="agreement_id",
        domain=[("is_template", "=", False)],
        help="Coverage templates related to this agreement",
    )
