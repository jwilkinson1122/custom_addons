# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_directions(models.Model):
    _name = 'podiatry.directions'
    _description = 'Medical Directions'
    _rec_name = 'podiatry_directions_pathology_id'

    podiatry_directions_pathology_id = fields.Many2one(
        'podiatry.pathology', 'Pathology')
    patient_evaluation_id = fields.Many2one(
        'podiatry.patient.evaluation', 'Patient Evaluation')
    comments = fields.Char('Comments')
