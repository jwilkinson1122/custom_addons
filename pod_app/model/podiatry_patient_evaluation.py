# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_patient_evaluation(models.Model):
    _name = 'podiatry.patient.evaluation'
    _description = 'podiatry patient evaluation'
    _rec_name = 'podiatry_patient_id'

    patient_id = fields.Many2one('res.partner', domain=[
                                 ('is_patient', '=', True)], string="Patient")
    podiatry_patient_id = fields.Many2one(
        'podiatry.patient', string="Patient", required=True)
    evaluation_date = fields.Datetime(string="Evaluation Date")
    physician_partner_id = fields.Many2one(
        'res.partner', domain=[('is_doctor', '=', True)], string="Doctor")
    primary_complaint = fields.Char('Primary Complaint')
    information_source = fields.Char('Source')
    present_condition = fields.Text(string='Present Condition')

    weight = fields.Float(string='Weight (lbs)', help='Weight in lbs')
    height = fields.Float(string='Height (in)')
    evaluation_summary = fields.Text(string='Evaluation Summary')
    symptom_pain = fields.Boolean('Pain')
    symptom_pain_intensity = fields.Integer('Pain intensity')
    signs_and_symptoms_ids = fields.One2many(
        'podiatry.signs.and.sympotoms', 'patient_evaluation_id', 'Signs and Symptoms')
    info_diagnosis = fields.Text(string='Information on Diagnosis')
    directions = fields.Text(string='Treatment Plan')
    user_id = fields.Many2one('res.users', 'Doctor user ID', readonly=True)
    podiatry_evaluation_date_id = fields.Many2one(
        'podiatry.evaluation', 'Evaluation Date')
    derived_from_physician_id = fields.Many2one(
        'podiatry.physician', 'Derived from Doctor')
    derived_to_physician_id = fields.Many2one(
        'podiatry.physician', 'Derived to Doctor')
    secondary_conditions_ids = fields.One2many(
        'podiatry.secondary_condition', 'patient_evaluation_id', 'Secondary Conditions')
