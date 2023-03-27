# -*- coding: utf-8 -*-
# from odoo import http


# class PrescriptionOrderAhmadyd(http.Controller):
#     @http.route('/prescription_order_ahmadyd/prescription_order_ahmadyd/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prescription_order_ahmadyd/prescription_order_ahmadyd/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prescription_order_ahmadyd.listing', {
#             'root': '/prescription_order_ahmadyd/prescription_order_ahmadyd',
#             'objects': http.request.env['prescription_order_ahmadyd.prescription_order_ahmadyd'].search([]),
#         })

#     @http.route('/prescription_order_ahmadyd/prescription_order_ahmadyd/objects/<model("prescription_order_ahmadyd.prescription_order_ahmadyd"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prescription_order_ahmadyd.object', {
#             'object': obj
#         })
