# -*- coding: utf-8 -*-
# from odoo import http


# class PrescriptionManagement(http.Controller):
#     @http.route('/prescription_management/prescription_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prescription_management/prescription_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('prescription_management.listing', {
#             'root': '/prescription_management/prescription_management',
#             'objects': http.request.env['prescription_management.prescription_management'].search([]),
#         })

#     @http.route('/prescription_management/prescription_management/objects/<model("prescription_management.prescription_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prescription_management.object', {
#             'object': obj
#         })
