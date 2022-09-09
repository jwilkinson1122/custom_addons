# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class podiatry_pathology(models.Model):
    _name = 'podiatry.pathology'
    _description = 'podiatry pathology'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one(
        'podiatry.pathology.category', string="Condition Category")
    line_ids = fields.One2many(
        'podiatry.pathology.group.member', 'condition_group_id', string="Group")
    chromosome = fields.Char(string="Affected Chromosome")
    gene = fields.Char(string="Gene")
    protein = fields.Char(string="Protein")
    info = fields.Text(string="Extra Info")
