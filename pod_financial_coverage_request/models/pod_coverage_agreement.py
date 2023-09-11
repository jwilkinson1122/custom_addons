from odoo import fields, models


class PodiatryCoverageAgreement(models.Model):
    _inherit = "pod.coverage.agreement"

    authorization_method_id = fields.Many2one(
        "pod.authorization.method", required=True
    )
    authorization_format_id = fields.Many2one(
        "pod.authorization.format", required=True
    )
