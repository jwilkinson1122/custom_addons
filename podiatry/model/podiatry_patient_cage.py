# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class podiatry_patient_cage(models.Model):
    _name = 'podiatry.patient.cage'
    _description = 'podiatry patient cage'
    _rec_name = 'patient_id'

    @api.onchange('cage_c', 'cage_a', 'cage_g', 'cage_e')
    def get_score(self):
        self.cage_score = int(self.cage_c)  + int(self.cage_a)  + int(self.cage_g) + int(self.cage_e)
         
    patient_id = fields.Many2one('podiatry.patient')
    evaluation_date = fields.Datetime()
    cage_c = fields.Boolean(default  = False)
    cage_a = fields.Boolean(default  = False)
    cage_g = fields.Boolean(default  = False)
    cage_e = fields.Boolean(default  = False)
    cage_score = fields.Integer('Cage Score',  default = 0)


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
