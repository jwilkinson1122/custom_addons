# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class PodiatryCoverageAgreement(models.Model):
    _inherit = "pod.coverage.agreement"

    authorization_method_id = fields.Many2one(
        "pod.authorization.method", required=True
    )
    authorization_format_id = fields.Many2one(
        "pod.authorization.format", required=True
    )
