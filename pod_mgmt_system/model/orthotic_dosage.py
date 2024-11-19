# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class orthotic_dosage(models.Model):
    _name = "orthotic.dosage"
    _description = "pod orthotic dosage"

    name = fields.Char(string="Frequency", required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")
