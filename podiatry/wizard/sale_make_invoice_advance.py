 
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, so_line)
        if order.type_id.journal_id:
            res["journal_id"] = order.type_id.journal_id.id
        if order.type_id:
            res["sale_type_id"] = order.type_id.id
        return res
