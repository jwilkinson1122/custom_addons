# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController as Configurator

class ProductReConfigurator(Configurator):

    @http.route()
    def configure(self, product_template_id, pricelist_id, **kw):
        add_qty = int(kw.get('add_qty', 1))
        product_template = request.env['product.template'].browse(int(product_template_id))
        
        # Getting attribute exclusions from the product template
        attribute_exclusions = product_template._get_attribute_exclusions()
        
        to_currency = product_template.currency_id
        pricelist = self._get_pricelist(pricelist_id)

        if pricelist:
            product_template = product_template.with_context(pricelist=pricelist.id, partner=request.env.user.partner_id)
            to_currency = pricelist.currency_id
        
        # template = 'sale.product_configurator_configure'
        template = 'sale_product_configurator.configure'
        order_line_id = kw.get('order_line_id')
        attribute_value_ids = []
        product_custome_values = {}
        if order_line_id:
            order_line = request.env['sale.order.line'].browse(order_line_id)
            add_qty = order_line.product_uom_qty
            attribute_value_ids += order_line.product_no_variant_attribute_value_ids.mapped('product_attribute_value_id.id')
            for product_custom_attribute in order_line.product_custom_attribute_value_ids:
                product_custome_values[product_custom_attribute.attribute_value_id.id] = product_custom_attribute.custom_value

            template = "product_reconfigurator.product_configurator_configure"

        product_product_id = kw.get('product_product_id')
        if product_product_id:
            product_product = request.env['product.product'].browse(product_product_id)
            attribute_value_ids += product_product.attribute_value_ids.ids
        order_id = kw.get('order_id')

        return request.env['ir.ui.view']._render_template(template, {
            'product': product_template,
            'to_currency': to_currency,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'get_attribute_exclusions': attribute_exclusions,  # Passing the result to the template
            'attribute_value_ids': attribute_value_ids,
            'order_id': order_id,
            'order_line_id': order_line_id,
            'product_custome_values': product_custome_values
        })

    @http.route(['/product_configurator/update_order'], type='json', auth="user", methods=['POST'])
    def update_order_line(self, order_id, order_line_id, **kwargs):
        order = request.env['sale.order'].browse(order_id)
        order.update_order_line(order_line_id, kwargs)
