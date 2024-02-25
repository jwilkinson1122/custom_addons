from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule(self, products, quantity, uom=None, date=False, **kwargs):
        """Overwrite for covering the case where templates are passed and a
        different uom is used."""
        if products[0]._name != "product.template":
            # Standard use case - Nothing to do
            return super(ProductPricelist, self)._compute_price_rule(
                products,
                quantity,
                date=date,
                uom=uom,
            )
        # Isolate object
        pricelist_obj = self

        if not uom and pricelist_obj.env.context.get("uom"):
            ctx = dict(pricelist_obj.env.context)
            # Remove uom context for avoiding the re-processing
            pricelist_obj = pricelist_obj.with_context(**ctx)

        return super(ProductPricelist, pricelist_obj)._compute_price_rule(
            products,
            quantity,
            date=date,
            uom=False,
        )

    def template_price_get(self, prod_id, quantity, partner=None):
        return {
            key: price[0]
            for key, price in self.template_price_rule_get(
                prod_id, quantity, partner=partner
            ).items()
        }

    def template_price_rule_get(self, prod_id, quantity, partner=None):
        return self._compute_price_rule_multi(prod_id, quantity)[prod_id.id]
