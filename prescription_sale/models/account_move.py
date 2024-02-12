from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_cancel(self):
        """If this a refund linked to an Prescription, undo the linking of the reception move for
        having proper quantities and status.
        """
        for prescription in self.env["prescription"].search([("refund_id", "in", self.ids)]):
            if prescription.sale_line_id:
                prescription._unlink_refund_with_reception_move()
        return super().button_cancel()

    def button_draft(self):
        """Relink the reception move when passing the refund again to draft."""
        for prescription in self.env["prescription"].search([("refund_id", "in", self.ids)]):
            if prescription.sale_line_id:
                prescription._link_refund_with_reception_move()
        return super().button_draft()

    def unlink(self):
        """If the invoice is removed, rollback the quantities correction"""
        for prescription in self.invoice_line_ids.prescription_id.filtered("sale_line_id"):
            prescription._unlink_refund_with_reception_move()
        return super().unlink()
