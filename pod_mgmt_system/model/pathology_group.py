# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class pathology_group(models.Model):
    _name = "pathology.group"
    _description = "pod pathology group"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")
    desc = fields.Char(string="Short Description", required=True)
    info = fields.Text(string="Detailed Information")
