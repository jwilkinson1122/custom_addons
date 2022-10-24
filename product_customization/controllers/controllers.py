# -*- coding: utf-8 -*-
# from odoo import http


# class ProductCustomization(http.Controller):
#     @http.route('/product_customization/product_customization', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_customization/product_customization/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_customization.listing', {
#             'root': '/product_customization/product_customization',
#             'objects': http.request.env['product_customization.product_customization'].search([]),
#         })

#     @http.route('/product_customization/product_customization/objects/<model("product_customization.product_customization"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_customization.object', {
#             'object': obj
#         })
