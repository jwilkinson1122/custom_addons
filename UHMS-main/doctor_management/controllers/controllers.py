# -*- coding: utf-8 -*-
# from odoo import http


# class Test03(http.Controller):
#     @http.route('/test_03/test_03', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_03/test_03/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_03.listing', {
#             'root': '/test_03/test_03',
#             'objects': http.request.env['test_03.test_03'].search([]),
#         })

#     @http.route('/test_03/test_03/objects/<model("test_03.test_03"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_03.object', {
#             'object': obj
#         })
