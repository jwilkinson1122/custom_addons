# -*- coding: utf-8 -*-
# from odoo import http


# class AnimalManagement(http.Controller):
#     @http.route('/animal_management/animal_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/animal_management/animal_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('animal_management.listing', {
#             'root': '/animal_management/animal_management',
#             'objects': http.request.env['animal_management.animal_management'].search([]),
#         })

#     @http.route('/animal_management/animal_management/objects/<model("animal_management.animal_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('animal_management.object', {
#             'object': obj
#         })
