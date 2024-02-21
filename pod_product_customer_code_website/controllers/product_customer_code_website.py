# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


class WebsiteSaleVariantControllerCustomerCode(WebsiteSaleVariantController):

    @http.route()
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        res = super(WebsiteSaleVariantControllerCustomerCode,self).get_combination_info_website(product_template_id,product_id,combination,add_qty,**kw)
        product_id = request.env['product.product'].sudo().browse(res.get('product_id'))

        if product_id and request.env.user._is_public() == False:
            customer_code = request.env['product.customer.info'].sudo().search(
                [('name', '=', request.env.user.partner_id.id), ('product_id', '=', product_id.id)], limit=1)
            if customer_code:
                res.update({'customer_code':customer_code.product_code})
                res.update({'product_name':customer_code.product_name})
        return res
