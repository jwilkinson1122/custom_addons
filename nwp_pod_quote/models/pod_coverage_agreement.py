# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PodiatryCoverageAgreement(models.Model):

    _inherit = "pod.coverage.agreement"

    quote_ids = fields.One2many("pod.quote", inverse_name="origin_agreement_id")
