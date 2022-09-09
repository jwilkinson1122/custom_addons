# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_diagnostic_hypotesis(models.Model):
    _name = 'podiatry.diagnostic_hypotesis'
    _description = 'podiatry diagnostic hypotesis'
    _rec_name = 'diagnostic_pathology_id'

    diagnostic_pathology_id = fields.Many2one(
        'podiatry.pathology', 'Procedure')
    patient_evaluation_id = fields.Many2one(
        'podiatry.patient.evaluation', 'Patient Evaluation')
    comments = fields.Char('Comments')
