# -*- coding: utf-8 -*-
# from odoo import http


# class PrescriptionOrder(http.Controller):
#     @http.route('/prescription_order/prescription_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prescription_order/prescription_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prescription_order.listing', {
#             'root': '/prescription_order/prescription_order',
#             'objects': http.request.env['prescription_order.prescription_order'].search([]),
#         })

#     @http.route('/prescription_order/prescription_order/objects/<model("prescription_order.prescription_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prescription_order.object', {
#             'object': obj
#         })
