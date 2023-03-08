# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _check_company_auto = True

    optional_product_ids = fields.Many2many(
        'product.template', 'product_optional_rel', 'src_id', 'dest_id',
        string='Optional Products', help="Optional Products are suggested "
        "whenever the customer hits *Add to Cart* (cross-sell strategy, "
        "e.g. for computers: warranty, software, etc.).", check_company=True)

    @api.depends('attribute_line_ids.value_ids.is_custom', 'attribute_line_ids.attribute_id.create_variant')
    def _compute_has_configurable_attributes(self):
        """ A product is considered configurable if:
        - It has dynamic attributes
        - It has any attribute line with at least 2 attribute values configured
        - It has at least one custom attribute value """
        for product in self:
            product.has_configurable_attributes = any(attribute.create_variant == 'dynamic' for attribute in product.mapped('attribute_line_ids.attribute_id')) \
                or any(len(attribute_line_id.value_ids) >= 2 for attribute_line_id in product.attribute_line_ids) \
                or any(attribute_value.is_custom for attribute_value in product.mapped('attribute_line_ids.value_ids'))

    def get_single_product_variant(self):
        """ Method used by the product configurator to check if the product is configurable or not.

        We need to open the product configurator if the product:
        - is configurable (see has_configurable_attributes)
        - has optional products """
        self.ensure_one()
        res = super(ProductTemplate, self).get_single_product_variant()
        if res.get('product_id', False):
            has_optional_products = False
            for optional_product in self.product_variant_id.optional_product_ids:
                if optional_product.has_dynamic_attributes() or optional_product._get_possible_variants(self.product_variant_id.product_template_attribute_value_ids):
                    has_optional_products = True
                    break
            res.update({'has_optional_products': has_optional_products})
        return res

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        """ Return info about a given combination.

        Note: this method does not take into account whether the combination is
        actually possible.

        :param combination: recordset of `product.template.attribute.value`

        :param product_id: id of a `product.product`. If no `combination`
            is set, the method will try to load the variant `product_id` if
            it exists instead of finding a variant based on the combination.

            If there is no combination, that means we definitely want a
            variant and not something that will have no_variant set.

        :param add_qty: float with the quantity for which to get the info,
            indeed some pricelist rules might depend on it.

        :param pricelist: `product.pricelist` the pricelist to use
            (can be none, eg. from SO if no partner and no pricelist selected)

        :param parent_combination: if no combination and no product_id are
            given, it will try to find the first possible combination, taking
            into account parent_combination (if set) for the exclusion rules.

        :param only_template: boolean, if set to True, get the info for the
            template only: ignore combination and don't try to find variant

        :return: dict with product/combination info:

            - product_id: the variant id matching the combination (if it exists)

            - product_template_id: the current template id

            - display_name: the name of the combination

            - price: the computed price of the combination, take the catalog
                price if no pricelist is given

            - list_price: the catalog price of the combination, but this is
                not the "real" list_price, it has price_extra included (so
                it's actually more closely related to `lst_price`), and it
                is converted to the pricelist currency (if given)

            - has_discounted_price: True if the pricelist discount policy says
                the price does not include the discount and there is actually a
                discount applied (price < list_price), else False
        """
        self.ensure_one()
        # get the name before the change of context to benefit from prefetch
        display_name = self.display_name

        display_image = True
        quantity = self.env.context.get('quantity', add_qty)
        context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
        product_template = self.with_context(context)

        combination = combination or product_template.env['product.template.attribute.value']

        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)

        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)

        if product:
            # We need to add the price_extra for the attributes that are not
            # in the variant, typically those of type no_variant, but it is
            # possible that a no_variant attribute is still in a variant if
            # the type of the attribute has been changed after creation.
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in combination.filtered(
                    lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                )
            ]
            if no_variant_attributes_price_extra:
                product = product.with_context(
                    no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                )
            list_price = product.price_compute('list_price')[product.id]
            price = product.price if pricelist else list_price
            display_image = bool(product.image_128)
            display_name = product.display_name
            price_extra = (product.price_extra or 0.0 ) + (sum(no_variant_attributes_price_extra) or 0.0)
        else:
            current_attributes_price_extra = [v.price_extra or 0.0 for v in combination]
            product_template = product_template.with_context(current_attributes_price_extra=current_attributes_price_extra)
            price_extra = sum(current_attributes_price_extra)
            list_price = product_template.price_compute('list_price')[product_template.id]
            price = product_template.price if pricelist else list_price
            display_image = bool(product_template.image_128)

            combination_name = combination._get_combination_name()
            if combination_name:
                display_name = "%s (%s)" % (display_name, combination_name)

        if pricelist and pricelist.currency_id != product_template.currency_id:
            list_price = product_template.currency_id._convert(
                list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )
            price_extra = product_template.currency_id._convert(
                price_extra, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )

        price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
        has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1

        return {
            'product_id': product.id,
            'product_template_id': product_template.id,
            'display_name': display_name,
            'display_image': display_image,
            'price': price,
            'list_price': list_price,
            'price_extra': price_extra,
            'has_discounted_price': has_discounted_price,
        }
