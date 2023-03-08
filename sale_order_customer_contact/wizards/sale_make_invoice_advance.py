from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        # Handling for when invoicing a down payment
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )

        if order.customer_contact_id:
            invoice.customer_contact_id = order.customer_contact_id.id

        return invoice
