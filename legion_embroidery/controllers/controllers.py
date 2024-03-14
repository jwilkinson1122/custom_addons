# -*- coding: utf-8 -*-
# from odoo import http


# class LegionEmbroidery(http.Controller):
#     @http.route('/legion_embroidery/legion_embroidery/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/legion_embroidery/legion_embroidery/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('legion_embroidery.listing', {
#             'root': '/legion_embroidery/legion_embroidery',
#             'objects': http.request.env['legion_embroidery.legion_embroidery'].search([]),
#         })

#     @http.route('/legion_embroidery/legion_embroidery/objects/<model("legion_embroidery.legion_embroidery"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('legion_embroidery.object', {
#             'object': obj
#         })
