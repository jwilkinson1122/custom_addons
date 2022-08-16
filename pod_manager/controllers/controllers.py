# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class KmPractice(http.Controller):

    @http.route('/patient_webform', type='http', auth='user', website=True)
    def patient_webform(self, **kw):
        return http.request.render('pod_manager.create_patient', {})

    @http.route('/create/webpatient', type="http", auth="user", website=True)
    def create_webpatient(self, **kw):
        # print("\nData Received.....", kw)
        request.env['pod.manager.patient'].sudo().create(kw)
        return request.render("pod_manager.patient_thanks", {})

    # route for show all the patient information
    @http.route('/patient_view', type='http', auth='public', website=True)
    def view_patient_web(self, **kw):
        patients = request.env['pod.manager.patient'].sudo().search([])
        # print("\nData Received.....", patients)
        return http.request.render('pod_manager.view_patient', {
            'patients': patients
        })

    # route for prescription website
    @http.route('/prescription_webform', type='http', auth='user', website=True)
    def prescription_webform(self, **kw):
        patient_rec = request.env['pod.manager.patient'].sudo().search([])
        doctor_rec = request.env['pod.manager.doctor'].sudo().search([])
        return http.request.render('pod_manager.create_prescription', {
            'patient_rec': patient_rec,
            'doctor_rec': doctor_rec
        })

    @http.route('/create/webprescription', type="http", auth="user", website=True)
    def create_webprescription(self, **kw):
        print("\nData Received.....", kw)
        request.env['pod.manager.prescription'].sudo().create(kw)
        return request.render("pod_manager.prescription_thanks", {})
