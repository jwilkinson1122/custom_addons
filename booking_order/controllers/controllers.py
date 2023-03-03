# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from odoo.addons.sale_booking_order.controllers.main import ProductConfiguratorController as Configurator


class ProductReConfigurator(Configurator):

    @http.route()
    def configure(self, product_id, pricelist_id, **kw):
        add_qty = int(kw.get('add_qty', 1))
        product_template = request.env['product.template'].browse(int(product_id))
        to_currency = product_template.currency_id
        pricelist = self._get_pricelist(pricelist_id)

        if pricelist:
            product_template = product_template.with_context(pricelist=pricelist.id, partner=request.env.user.partner_id)
            to_currency = pricelist.currency_id
        template = 'sale.product_configurator_configure'
        order_line_id = kw.get('order_line_id')
        attribute_value_ids = []
        product_custom_values = {}
        if order_line_id:
            order_line = request.env['sale.order.line'].browse(order_line_id)
            add_qty = order_line.product_uom_qty
            # get no variant attributes
            attribute_value_ids += order_line.product_no_variant_attribute_value_ids.mapped('product_attribute_value_id.id')
            for product_custom_attribute in order_line.product_custom_attribute_value_ids:
                product_custom_values[product_custom_attribute.attribute_value_id.id] = product_custom_attribute.custom_value

            template = "booking_order.product_configurator_configure"

        product_product_id = kw.get('product_product_id')
        if product_product_id:
            product_product = request.env['product.product'].browse(product_product_id)
            attribute_value_ids += product_product.attribute_value_ids.ids
        order_id = kw.get('order_id')

        return request.env['ir.ui.view'].render_template(template, {
            'product': product_template,
            'to_currency': to_currency,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'get_attribute_exclusions': self._get_attribute_exclusions,
            'attribute_value_ids': attribute_value_ids,
            'order_id': order_id,
            'order_line_id': order_line_id,
            'product_custom_values': product_custom_values
        })

    @http.route(['/product_configurator/update_order'], type='json', auth="user", methods=['POST'])
    def update_order_line(self, order_id, order_line_id, **kwargs):
        order = request.env['sale.order'].browse(order_id)
        order.update_order_line(order_line_id, kwargs)
