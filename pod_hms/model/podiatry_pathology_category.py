# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_pathology_category(models.Model):
    _name = 'podiatry.pathology.category'
    _description = 'podiatry pathology category'
    # name = fields.Char(string="Category Name")
    name = fields.Char(string="Category Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one(
        'podiatry.pathology.category', string="Parent Category")
    code = fields.Char(string="Code")
