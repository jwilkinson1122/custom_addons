from odoo import _, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _prepare_invoice(self):
        # Handling for when invoicing the invoiceable lines
        self.ensure_one()
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if (
            self.customer_order_number
            and self.company_id.customer_order_number_to_invoice
        ):

            if not invoice_vals["narration"]:
                invoice_vals["narration"] = ""
            invoice_vals["narration"] += "\n{}: {}".format(
                _("Customer Order Number"), self.customer_order_number
            )
        return invoice_vals

    customer_order_number = fields.Char(
        string="Customer's Order Number",
        help="""If the customer has specified an order number of their own""",
    )
