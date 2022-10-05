# -*- coding: utf-8 -*-
from odoo import http

# class Patientclinic(http.Controller):
#     @http.route('/patient_clinic/patient_clinic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/patient_clinic/patient_clinic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('patient_clinic.listing', {
#             'root': '/patient_clinic/patient_clinic',
#             'objects': http.request.env['patient_clinic.patient_clinic'].search([]),
#         })

#     @http.route('/patient_clinic/patient_clinic/objects/<model("patient_clinic.patient_clinic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('patient_clinic.object', {
#             'object': obj
#         })
