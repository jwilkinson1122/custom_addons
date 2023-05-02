# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class signs_and_sympotoms(models.Model):
    _name = 'podiatry.signs.and.sympotoms'
    _description = 'podiatry signs and sympotoms'
    _rec_name = 'pathology_id'

    patient_details_id = fields.Many2one('podiatry.patient.details','Patient Details')
    pathology_id = fields.Many2one('podiatry.pathology','Sign or Symptom')
    sign_or_symptom = fields.Selection([
            ('sign', 'Sign'),
            ('symptom', 'Symptom'),
        ], string='Subjective / Objective')
    comments = fields.Char('Comments')


