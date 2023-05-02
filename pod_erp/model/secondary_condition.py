# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class secondary_condition(models.Model):
    _name = 'podiatry.secondary_condition'
    _description = 'podiatry secondary condition'
    _rec_name = 'pathology_id'

    patient_details_id = fields.Many2one('podiatry.patient.details','Patient Details')
    pathology_id = fields.Many2one('podiatry.pathology','Pathology')
    comments = fields.Char('Comments')

