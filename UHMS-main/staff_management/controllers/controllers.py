# -*- coding: utf-8 -*-
# from odoo import http


# class Test04(http.Controller):
#     @http.route('/test_04/test_04', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_04/test_04/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_04.listing', {
#             'root': '/test_04/test_04',
#             'objects': http.request.env['test_04.test_04'].search([]),
#         })

#     @http.route('/test_04/test_04/objects/<model("test_04.test_04"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_04.object', {
#             'object': obj
#         })
