# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        [
            ("delivered", "Regular invoice"),
            ("percentage", "Down payment (percentage)"),
            ("fixed", "Down payment (fixed amount)"),
        ],
        string="Create Invoice",
        default="delivered",
        required=True,
        help="""A standard invoice is issued with all the order lines ready for
        invoicing, according to their invoicing policy
        (based on ordered or delivered quantity).""",
    )

    def create_invoices(self):
        ctx = self.env.context.copy()
        if self._context.get("active_model") == "podiatry.prescription":

            PodiatryPrescription = self.env["podiatry.prescription"]
            prescription = PodiatryPrescription.browse(self._context.get("active_ids", []))
            prescription.device_line_ids.mapped("product_id").write({"isdevice": True})
            ctx.update(
                {
                    "active_ids": prescription.order_id.ids,
                    "active_id": prescription.order_id.id,
                    "prescription_id": prescription.id,
                }
            )
        res = super(SaleAdvancePaymentInv, self.with_context(**ctx)).create_invoices()

        return res
