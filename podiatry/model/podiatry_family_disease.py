# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class podiatry_family_disease(models.Model):
    _name = 'podiatry.family.disease'
    _description = 'Podiatry Family Disease'
    _rec_name = 'podiatry_pathology_id'

    podiatry_pathology_id = fields.Many2one('podiatry.pathology', 'Disease',required=True)
    relative = fields.Selection([('m','Mother'), ('f','Father'), ('b', 'Brother'), ('s', 'Sister'), ('a', 'aunt'), ('u', 'Uncle'), ('ne', 'Nephew'), ('ni', 'Niece'), ('gf', 'GrandFather'), ('gm', 'GrandMother')],string="Relative")
    metrnal = fields.Selection([('m', 'Maternal'),('p', 'Paternal')],string="Maternal")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: