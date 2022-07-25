# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class pod_pathology(models.Model):
    _name = 'pod.pathology'
    _description = 'pod pathology'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one(
        'pod.pathology.category', string="Condition Category")
    line_ids = fields.One2many(
        'pod.pathology.group.member', 'condition_group_id', string="Group")
    info = fields.Text(string="Extra Info")
