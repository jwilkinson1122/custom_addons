# -*- coding: utf-8 -*-

from odoo import _, fields, models


class product_template(models.Model):
    """
    Overwrite to the case when a variant is only to create
    """
    _inherit = "product.template"

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
        res = super(product_template, self)._get_product_price_context(combination)
        res.update({
            "current_attributes_price_extra_advanced": combination,
            "current_attributes_price_extra": 0,
        })
        return res

    def _get_attributes_extra_price(self):
        """
        Re-write  the method to calculate the difference between a standard price and its formula-based price

        Extra info:
         * Expected singleton

        Methods:
         * _calculate_price of product.template.attribute.value

        Returns:
         * float
        """
        standard_price = new_price = self.list_price or 0.0
        if self._context.get("current_attributes_price_extra_advanced"):
            new_price = self._context.get("current_attributes_price_extra_advanced")._calculate_price(standard_price)
        return new_price - standard_price

    def action_open_attribute_values_advanced(self):
        """
        The method to open the full list of attribute values to manage sequence
        """
        all_template_values = self.attribute_line_ids.mapped("product_template_value_ids")
        return {
            "type": "ir.actions.act_window",
            "name": _("Product Variant Values"),
            "res_model": "product.template.attribute.value",
            "view_mode": "tree,form",
            "domain": [("id", "in", all_template_values.ids)],
            "views": [
                (self.env.ref("product.product_template_attribute_value_view_tree").id, "list"),
                (self.env.ref("product.product_template_attribute_value_view_form").id, "form"),
            ],
            "context": {"search_default_active": 1},
        }
