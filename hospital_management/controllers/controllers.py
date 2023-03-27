# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json

class HospitalManagement(http.Controller):
    @http.route('/patients', type="http", auth='user', website=True)
    def index(self, **kw):
        patients = request.env['hospital.patient'].search([])
        context = {
            'patients': patients
        }
        return request.render('hospital_management.index_page', context)

    @http.route('/patient/create', type="http", auth='user', website=True)
    def create(self, **kw):
        if request.httprequest.method == 'POST':
            patient_obj = request.env['hospital.patient']
            responsible = request.env['res.partner'].search(
                [('name', '=', kw.get('responsible'))])
            res = patient_obj.create({
                'name': kw.get('name'),
                'age': kw.get('age'),
                'responsible_id': responsible.id,
                'note': kw.get('note'),
            })
            if res.exists():
                return request.redirect("/patients")

        responsibles = request.env['res.partner'].search(
            [('is_company', '=', True)])
        context = {
            'responsibles': responsibles
        }
        return request.render('hospital_management.create_page', context)

    @http.route('/patient/update/<int:id>', type="http", auth='user', website=True)
    def update(self, id, **kw):

        record = request.env['hospital.patient'].browse(id)

        if request.httprequest.method == 'POST':
            res = record.write({
                'name': kw.get('name'),
                'age': kw.get('age'),
                'responsible_id': kw.get('responsible'),
                'note': kw.get('note'),
            })
            if res:
                return request.redirect("/patients")
            
        responsibles = request.env['res.partner'].search([('is_company', '=', True)])
        context = {
            'responsibles':responsibles,
            'record':record
        }
        return request.render('hospital_management.update_page', context)


    @http.route('/patient/delete/<int:id>', type="http", auth='user', website=True)
    def delete(self, id):
        record = request.env['hospital.patient'].browse(id)
        record.unlink()
        return request.redirect("/patients")

    

    @http.route('/patient-list', type="http", auth='public')
    def show_patient_list(self, **kw):
        print("kw:", kw)
        patients = request.env['hospital.patient'].search([])
        patient_list = []
        for patient in patients:
            vals = {
                'name':patient.name
            }
            patient_list.append(vals)
        #return json.dumps(patient_list)
        return Response(json.dumps(patient_list), status=500)
    

    
    