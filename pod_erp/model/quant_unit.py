# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class quant_unit(models.Model):
    _name = 'podiatry.quant.unit'
    _description = 'Podiatry Quantity Unit'

    name = fields.Char(string="Unit",required=True)
    description = fields.Char(string="Description")

