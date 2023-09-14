

from odoo import fields, models


class PodiatryCoverageAgreementItem(models.Model):
    _inherit = "pod.coverage.agreement.item"

    invoice_group_method_id = fields.Many2one("invoice.group.method")

    def _check_authorization(self, method, **kwargs):
        vals = super()._check_authorization(method, **kwargs)
        if method.force_item_authorization_method and self.invoice_group_method_id:
            vals["invoice_group_method_id"] = self.invoice_group_method_id.id
        if "invoice_group_method_id" not in vals:
            vals["invoice_group_method_id"] = (
                method.invoice_group_method_id.id
                or self.coverage_agreement_id.invoice_group_method_id.id
            )
        return vals
