from odoo import _, models


class SaleAdvancePaymentInv(models.TransientModel):

    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        # Handling for when invoicing a down payment
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(
            order, so_line, amount
        )

        if (
            order.customer_order_number
            and order.company_id.customer_order_number_to_invoice
        ):
            invoice.narration = "{}{}: {}".format(
                invoice.narration and (invoice.narration + "\n") or "",
                _("Customer Order Number"),
                order.customer_order_number,
            )

        return invoice
