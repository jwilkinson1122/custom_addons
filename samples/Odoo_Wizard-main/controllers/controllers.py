# -*- coding: utf-8 -*-
# from odoo import http


# class WizMod(http.Controller):
#     @http.route('/wiz_mod/wiz_mod', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wiz_mod/wiz_mod/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('wiz_mod.listing', {
#             'root': '/wiz_mod/wiz_mod',
#             'objects': http.request.env['wiz_mod.wiz_mod'].search([]),
#         })

#     @http.route('/wiz_mod/wiz_mod/objects/<model("wiz_mod.wiz_mod"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wiz_mod.object', {
#             'object': obj
#         })

