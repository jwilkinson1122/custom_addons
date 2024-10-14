# -*- coding: utf-8 -*-

import itertools
from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.product'

    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """
        :return: Display product variant list based on the selected Product Template
        """
        domain = domain or []
        if self._context.get('product_tmplt_id'):
            product_ids = self._search([('product_tmpl_id', '=', self._context['product_tmplt_id'])], limit=limit,
                                       order=order)
            return product_ids
        return super(Product, self)._name_search(name, domain, operator, limit, order)

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        """
        :return: Display Product variant list on Search More wizard based on the selected Product template
        """
        domain = domain or []
        if self._context.get('product_tmplt_id'):
            domain += ([('product_tmpl_id', '=', self._context['product_tmplt_id'])])
            return super().web_search_read(domain=domain, specification=specification, offset=offset, limit=limit,
                                           order=order, count_limit=count_limit)
        return super().web_search_read(domain=domain, specification=specification, offset=offset, limit=limit,
                                       order=order, count_limit=count_limit)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inventory_product_add_mode = fields.Selection(
        selection=[
            ('normal', 'Normal Entry'),
            ('matrix', "Order Grid Entry"),
            ('product_configurator', "Product Configurator")
        ],
        string="Inventory add product mode",
        default='normal',
        help="Normal Entry: choose attribute values to add the matching product variant to the stock."
             "\nGrid: add several variants at once from the grid of attribute values"
             "\nVariant Grid: add several variants in list view type at once from the grid of attribute values")

    def get_single_product_variant(self):
        res = super().get_single_product_variant()
        res['mode'] = ""
        return res

    def _get_template_matrix(self, **kwargs):
        """
        :return: header & matrix when product_configurator option is selected on inventory_product_add_mode field
        """
        res = super(ProductTemplate, self)._get_template_matrix(**kwargs)
        matrix2 = []
        header = {}
        res_model = self._context.get('res_model')

        if res_model == 'stock.picking' and self.inventory_product_add_mode == 'product_configurator':
            header = [{"name": self.display_name}] + [{'name': "Quantity"}]
            attribute_lines = self.valid_product_template_attribute_line_ids
            Attrib = self.env['product.template.attribute.value']
            first_line_attributes = attribute_lines[0].product_template_value_ids._only_active()
            attribute_ids_by_line = [line.product_template_value_ids._only_active().ids for line in attribute_lines]

            result = [[]]
            for pool in attribute_ids_by_line:
                result = [x + [y] for y in pool for x in result]
            args = [iter(result)] * len(first_line_attributes)
            rows = itertools.zip_longest(*args)

            for row in rows:
                for cell in row:
                    row_attributes = Attrib.browse(cell)
                    row_header_cell = {
                        'name': ' • '.join([attr.display_name for attr in row_attributes]) if row_attributes else " "
                    }
                    result = [row_header_cell]

                    combination = Attrib.browse(cell)
                    is_possible_combination = self._is_combination_possible(combination)
                    cell.sort()
                    result.append({
                        "ptav_ids": cell,
                        "qty": 0,
                        "is_possible_combination": is_possible_combination
                    })
                    matrix2.append(result)
            res['matrix'] = matrix2
            res['header'] = header
        return res
