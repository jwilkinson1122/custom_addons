# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class pathology_group_member(models.Model):
    _name = "pathology.group.member"
    _description = "pod pathology group member"

    condition_group_id = fields.Many2one(
        "pathology.group", string="Group", required=True
    )
