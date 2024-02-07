
from odoo import models
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_prescription_invoice_lines_qty(self):
        """For those with differences, check if the kit quantity is the same"""
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        lines = super()._check_prescription_invoice_lines_qty()
        if lines:
            return lines.sudo().filtered(
                lambda r: (
                    r.prescription_id.phantom_bom_product
                    and float_compare(r.quantity, r.prescription_id.kit_qty, precision) < 0
                )
            )
        return lines
