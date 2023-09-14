

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    agreement_id = fields.Many2one(
        comodel_name="pod.coverage.agreement",
        string="Agreement",
        readonly=True,
    )
    coverage_template_id = fields.Many2one("pod.coverage.template", readonly=True)
    invoice_group_method_id = fields.Many2one("invoice.group.method", readonly=True)

    def _get_refund_common_fields(self):
        return super()._get_refund_common_fields() + [
            "agreement_id",
            "coverage_template_id",
            "invoice_group_method_id",
        ]
