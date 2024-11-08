# -*- coding: utf-8 -*-
# from odoo import http


# class Test01(http.Controller):
#     @http.route('/test_01/test_01', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_01/test_01/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_01.listing', {
#             'root': '/test_01/test_01',
#             'objects': http.request.env['test_01.test_01'].search([]),
#         })

#     @http.route('/test_01/test_01/objects/<model("test_01.test_01"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_01.object', {
#             'object': obj
#         })
