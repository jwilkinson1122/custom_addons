# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PodiatryServiceType(models.Model):
    _name = 'podiatry.service.type'
    _description = 'Podiatry Service Type'

    name = fields.Char(required=True, translate=True)
    category = fields.Selection([
        ('prescription', 'Prescription'),
        ('service', 'Service')
        ], 'Category', required=True, help='Choose whether the service refer to prescriptions, device services or both')
