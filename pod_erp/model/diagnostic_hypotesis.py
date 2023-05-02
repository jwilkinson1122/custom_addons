# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class diagnostic_hypotesis(models.Model):
    _name = 'podiatry.diagnostic_hypotesis'
    _description = 'podiatry diagnostic hypotesis'
    _rec_name = 'diagnostic_pathology_id'

    diagnostic_pathology_id = fields.Many2one('podiatry.pathology','Pathology')
    patient_details_id = fields.Many2one('podiatry.patient.details','Patient Details')
    comments = fields.Char('Comments')

