# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class directions(models.Model):
    _name = 'podiatry.directions'
    _description = 'Podiatry Directions'
    _rec_name = 'directions_pathology_id'

    directions_pathology_id = fields.Many2one('podiatry.pathology','Pathology')
    patient_details_id = fields.Many2one('podiatry.patient.details','Patient Details')
    comments = fields.Char('Comments')

