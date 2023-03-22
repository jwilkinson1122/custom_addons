# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_pathology(models.Model):
    _name = 'medical.pathology'
    _description = 'medical pathology'

    name = fields.Char(string="Name",required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one('medical.pathology.category',string="Condition Category")
    line_ids = fields.One2many('medical.pathology.group.member','condition_group_id',string="Group")
    info = fields.Text(string="Extra Info")