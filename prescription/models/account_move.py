
from odoo import _, fields, api, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountMove(models.Model):
    _inherit = "account.move"

    def _check_prescription_invoice_lines_qty(self):
        """We can't refund a different qty than the stated in the Prescription.
        Extend to change criteria"""
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return (
            self.sudo()
            .mapped("invoice_line_ids")
            .filtered(
                lambda r: (
                    r.prescription_id
                    and float_compare(r.quantity, r.prescription_id.product_uom_qty, precision)
                    < 0
                )
            )
        )

    def action_post(self):
        """Avoids to validate a refund with less quantity of product than
        quantity in the linked Prescription.
        """
        if self._check_prescription_invoice_lines_qty():
            raise ValidationError(
                _(
                    "There is at least one invoice lines whose quantity is "
                    "less than the quantity specified in its linked Prescription."
                )
            )
        return super().action_post()

    def unlink(self):
        prescription = self.mapped("invoice_line_ids.prescription_id")
        prescription.write({"state": "received"})
        return super().unlink()
    
    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("prescription_id"):
            prescription = self.env["prescription"].browse(self._context["prescription_id"])
            prescription.write({"prescription_invoice_id": res.id, "invoice_status": "invoiced"})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    prescription_id = fields.Many2one(
        comodel_name="prescription",
        string="Prescription",
    )
