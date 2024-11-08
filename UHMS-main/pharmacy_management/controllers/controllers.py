# -*- coding: utf-8 -*-
# from odoo import http


# class Test05(http.Controller):
#     @http.route('/test_05/test_05', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_05/test_05/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_05.listing', {
#             'root': '/test_05/test_05',
#             'objects': http.request.env['test_05.test_05'].search([]),
#         })

#     @http.route('/test_05/test_05/objects/<model("test_05.test_05"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_05.object', {
#             'object': obj
#         })
