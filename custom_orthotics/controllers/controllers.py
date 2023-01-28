# -*- coding: utf-8 -*-
from odoo import http

# class Patientclinic(http.Controller):
#     @http.route('/custom_orthotics/custom_orthotics/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_orthotics/custom_orthotics/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_orthotics.listing', {
#             'root': '/custom_orthotics/custom_orthotics',
#             'objects': http.request.env['custom_orthotics.custom_orthotics'].search([]),
#         })

#     @http.route('/custom_orthotics/custom_orthotics/objects/<model("custom_orthotics.custom_orthotics"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_orthotics.object', {
#             'object': obj
#         })
