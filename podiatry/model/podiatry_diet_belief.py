# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class podiatry_diet_belief(models.Model):
    _name = 'podiatry.diet.belief'
    _description='podiatry diet belief'

    code = fields.Char(string='Code',required=True)
    description = fields.Text(string='Description',required=True)
    name = fields.Char(string='Belief')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
