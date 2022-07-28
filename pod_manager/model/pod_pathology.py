# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class pod_pathology(models.Model):
    _name = 'pod.pathology'
    _description = 'podiatry pathology'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one(
        'pod.pathology.category', string="Pathology Category")
    line_ids = fields.One2many(
        'pod.pathology.group.member', 'condition_group_id', string="Group")
    chromosome = fields.Char(string="Affected Chromosome")
    gene = fields.Char(string="Gene")
    protein = fields.Char(string="Protein")
    info = fields.Text(string="Extra Info")
