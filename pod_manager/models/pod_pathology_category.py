# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_pathology_category(models.Model):
    _name = 'pod.pathology.category'
    _description = 'pod pathology category'

    name = fields.Char(string="Category Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one(
        'pod.pathology.category', string="Parent Category")
