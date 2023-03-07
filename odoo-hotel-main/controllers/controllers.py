# -*- coding: utf-8 -*-
# from odoo import http


# class HotelGrivia(http.Controller):
#     @http.route('/hotel_grivia/hotel_grivia/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hotel_grivia/hotel_grivia/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hotel_grivia.listing', {
#             'root': '/hotel_grivia/hotel_grivia',
#             'objects': http.request.env['hotel_grivia.hotel_grivia'].search([]),
#         })

#     @http.route('/hotel_grivia/hotel_grivia/objects/<model("hotel_grivia.hotel_grivia"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hotel_grivia.object', {
#             'object': obj
#         })
