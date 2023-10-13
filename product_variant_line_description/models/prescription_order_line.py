from odoo import api, models


class PrescriptionOrderLine(models.Model):
    _inherit = "pod.prescription.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(PrescriptionOrderLine, self).product_id_change()
        if self.product_id:
            product = self.product_id.with_context(lang=self.prescription_order_id.partner_id.lang)
            if product.variant_description:
                self.name = product.variant_description
        return res
