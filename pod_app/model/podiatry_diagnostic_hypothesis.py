# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_diagnostic_hypothesis(models.Model):
    _name = 'podiatry.diagnostic_hypothesis'
    _description = 'podiatry diagnostic hypothesis'
    _rec_name = 'diagnostic_pathology_id'

    diagnostic_pathology_id = fields.Many2one(
        'podiatry.pathology', 'Pathology')
    patient_evaluation_id = fields.Many2one(
        'podiatry.patient.evaluation', 'Patient Evaluation')
    comments = fields.Char('Comments')
