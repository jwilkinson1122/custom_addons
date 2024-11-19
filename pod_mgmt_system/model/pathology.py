# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class pathology(models.Model):
    _name = "pathology"
    _description = "pod pathology"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    category_id = fields.Many2one("pathology.category", string="Condition Category")
    line_ids = fields.One2many(
        "pathology.group.member", "condition_group_id", string="Group"
    )
    chromosome = fields.Char(string="Affected Chromosome")
    gene = fields.Char(string="Gene")
    protein = fields.Char(string="Protein")
    info = fields.Text(string="Extra Info")
