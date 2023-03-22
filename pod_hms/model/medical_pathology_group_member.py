# -*- coding: utf-8 -*-
# Part of NWPL. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_pathology_group_member(models.Model):
    _name = 'medical.pathology.group.member'
    _description = 'medical pathology group member'

    condition_group_id = fields.Many2one('medical.pathology.group', string="Group", required=True)
