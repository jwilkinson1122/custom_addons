from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            product = self.product_id.with_context(lang=self.order_id.partner_id.lang)
            if product.variant_description_sale:
                self.name = product.variant_description_sale

