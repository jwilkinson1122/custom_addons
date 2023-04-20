# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class podiatry_pathology_group_member(models.Model):
    _name = 'podiatry.pathology.group.member'
    _description = 'podiatry pathology group member'

    disease_group_id = fields.Many2one('podiatry.pathology.group', string="Group", required=True)
