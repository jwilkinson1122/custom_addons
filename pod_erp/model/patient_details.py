# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class patient_details(models.Model):
	_name = 'podiatry.patient.details'
	_description = 'podiatry patient details'
	_rec_name = 'patient_id' 

	patient_id = fields.Many2one('res.partner',domain=[('is_patient','=',True)],string="Patient")
	patient_id = fields.Many2one('podiatry.patient',string="Patient",required=True)
	physician_partner_id = fields.Many2one('res.partner',domain=[('is_doctor','=',True)],string="Doctor")
	weight = fields.Float(string='Weight (kg)',help='Weight in Kilos')
	height = fields.Float(string='Height (cm)')
	
	
	tag = fields.Integer(
			string='Last TAGs',
			help='Triacylglycerol(triglicerides) level. Can be approximative'
		)
	
	symptom_pain = fields.Boolean('Pain')
	symptom_pain_intensity = fields.Integer('Pain intensity')
	symptom_arthralgia = fields.Boolean('Arthralgia')
	symptom_abdominal_pain = fields.Boolean('Abdominal Pain')
	symptom_thoracic_pain = fields.Boolean('Thoracic Pain')
	symptom_pelvic_pain = fields.Boolean('Pelvic Pain')
	symptom_hoarseness = fields.Boolean('Hoarseness')
	symptom_sore_throat = fields.Boolean('Sore throat')
	diagnosis_id = fields.Many2one('podiatry.pathology','Presumptive Diagnosis')
	user_id = fields.Many2one('res.users','Doctor user ID',readonly=True)



