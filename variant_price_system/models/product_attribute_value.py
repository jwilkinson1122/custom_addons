# -*- coding: utf-8 -*-

from odoo import fields, models


class product_template_attribute_value(models.Model):
    """
    Overwrite to add extra and multiplier
    """
    _inherit = "product.template.attribute.value"

    def _compute_price_extra(self):
        """
        Force standard price_extra always be zero
        Needed to not show labels in product configurator and website
        """
        for ptav in self:
            ptav.price_extra = 0.0

    def _inverse_price_extra(self):
        """
        Update the price plus
        Needed to pass tests mainly
        """
        for ptav in self:
            ptav.price_plus = ptav.price_extra

    price_plus = fields.Float(string="Price Extra", digits="Product Price")
    price_multiple = fields.Float(string="Coefficient (%)", digits="Product Price")
    price_extra = fields.Float(
        compute=_compute_price_extra, inverse=_inverse_price_extra, store=False, string="Price Change",
    )
    sequence_esp = fields.Integer(string="Pricing Sequence", default=0)

    _order = "sequence_esp,product_attribute_value_id,id"


    def _calculate_price(self, price):
        """
        The method to apply formula for the given attribute values

        Args:
         * price - float

        Returns:
         * float
        """
        res_price = price
        if self:
            value_ids = self.sorted(lambda v: v.sequence_esp)
            for attr_value in value_ids:
                res_price = (res_price + attr_value.price_plus) * (1 + attr_value.price_multiple / 100)
        return res_price
