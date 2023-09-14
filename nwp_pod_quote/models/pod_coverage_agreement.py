

from odoo import fields, models


class PodiatryCoverageAgreement(models.Model):

    _inherit = "pod.coverage.agreement"

    quote_ids = fields.One2many("pod.quote", inverse_name="origin_agreement_id")
