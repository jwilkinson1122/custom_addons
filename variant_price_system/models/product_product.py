# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_product(models.Model):
    """
    Overwrite to calculate lst_price on attributes extra and coefficients
    """
    _inherit = "product.product"

    @api.depends("list_price", "esp_price", "product_template_attribute_value_ids.price_plus",
        "product_template_attribute_value_ids.price_multiple", "product_template_attribute_value_ids.sequence_esp")
    @api.depends_context("uom", "no_advanced_pricing")
    def _compute_product_lst_price(self):
        """
        Compute method for the attribute lst_price
        Re-written to add extra "depends" and recalculate price based on our own coefficients and surpluses

        Methods:
         * _get_price_advanced
        """
        super(product_product, self)._compute_product_lst_price()
        if not self._context.get("no_advanced_pricing"):
            for product in self:
                lst_price = product.lst_price - product.price_extra
                lst_price = product._get_price_advanced(lst_price)
                product.lst_price = lst_price + product.esp_price

    lst_price = fields.Float(compute=_compute_product_lst_price)
    esp_price = fields.Float(
        string="Variant Extra Beside Attributes",
        help="Besides attributes multipliers and extras",
        digits="Product Price",
    )

    def _get_product_price_context(self, combination):
        """
        Re-write to recalculate required context

        Returns:
         * dict

        Extra info:
         * Expected singleton
         * We use super (and no_variant_attributes_price_extra:0) just for a sudden case some module will try to pass
           additional context here
        """
        res = super(product_product, self)._get_product_price_context(combination)
        never_created_attributes = combination.filtered(
            lambda ptav: ptav.product_tmpl_id == self.product_tmpl_id
                and ptav not in self.product_template_attribute_value_ids
        )
        res.update({
            "no_variant_attributes_price_extra_advanced": never_created_attributes,
            "no_variant_attributes_price_extra": 0,
        })
        return res

    def _get_attributes_extra_price(self):
        """
        Re-write  the method to calculate the difference between a standard price and its formula-based price

        Extra info:
         * Expected singleton

        Returns:
         * float
        """
        standard_price = self.with_context(no_advanced_pricing=True).lst_price - self.price_extra
        new_price = self.lst_price
        return new_price - standard_price

    def _get_price_advanced(self, price=None):
        """
        The method to return prices with attributes coefficients

        Args:
         * price - basic price of product (list_price or pricelist adapted list_price)

        Methods:
         * _calculate_price of product.attribute.value

        Returns:
         * float

        Extra info:
         * Expected singleton
        """
        all_values = self.product_template_attribute_value_ids
        extra_advanced = self._context.get("no_variant_attributes_price_extra_advanced")
        if extra_advanced:
            # to the case of no_create attributes
            if isinstance(extra_advanced, list):
                # for the case we receive list of recordset in list
                now_recordset = self.env["product.template.attribute.value"]
                for extra in extra_advanced:
                    now_recordset += extra
                extra_advanced = now_recordset
            all_values += extra_advanced
        return all_values._calculate_price(price)
