from odoo import api, models


class PrescriptionOrderLine(models.Model):
    _inherit = "prescription.order.line"

    @api.onchange("product_id")
    def _onchange_product_id_warning(self):
        res = super(PrescriptionOrderLine, self)._onchange_product_id_warning()
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description_prescription:
                self.name = product.variant_description_prescription
        return res
