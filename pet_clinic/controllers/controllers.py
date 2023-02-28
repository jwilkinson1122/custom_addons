# -*- coding: utf-8 -*-
from odoo import http

# class Petclinic(http.Controller):
#     @http.route('/pet_clinic/pet_clinic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pet_clinic/pet_clinic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pet_clinic.listing', {
#             'root': '/pet_clinic/pet_clinic',
#             'objects': http.request.env['pet_clinic.pet_clinic'].search([]),
#         })

#     @http.route('/pet_clinic/pet_clinic/objects/<model("pet_clinic.pet_clinic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pet_clinic.object', {
#             'object': obj
#         })
