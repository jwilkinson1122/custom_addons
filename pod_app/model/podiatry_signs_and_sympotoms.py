# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_signs_and_sympotoms(models.Model):
    _name = 'podiatry.signs.and.sympotoms'
    _description = 'podiatry signs and sympotoms'
    _rec_name = 'pathology_id'

    patient_evaluation_id = fields.Many2one(
        'podiatry.patient.evaluation', 'Patient Evaluation')
    pathology_id = fields.Many2one('podiatry.pathology', 'Sign or Symptom')
    sign_or_symptom = fields.Selection([
        ('sign', 'Sign'),
        ('symptom', 'Symptom'),
    ], string='Subjective / Objective')
    comments = fields.Char('Comments')
