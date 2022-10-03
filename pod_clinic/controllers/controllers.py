# -*- coding: utf-8 -*-
from odoo import http

# class Patientclinic(http.Controller):
#     @http.route('/pod_clinic/pod_clinic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pod_clinic/pod_clinic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pod_clinic.listing', {
#             'root': '/pod_clinic/pod_clinic',
#             'objects': http.request.env['pod_clinic.pod_clinic'].search([]),
#         })

#     @http.route('/pod_clinic/pod_clinic/objects/<model("pod_clinic.pod_clinic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pod_clinic.object', {
#             'object': obj
#         })
