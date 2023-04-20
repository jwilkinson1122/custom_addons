# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class podiatry_dose_unit(models.Model):
    _name = 'podiatry.dose.unit'
    _description = 'Podiatry Dose Unit'

    name = fields.Char(string="Unit",required=True)
    description = fields.Char(string="Description")

