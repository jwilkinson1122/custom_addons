# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PodiatryDeviceState(models.Model):
    _name = 'podiatry.device.state'
    _order = 'sequence asc'
    _description = 'Device Status'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(help="Used to order the note stages")

    _sql_constraints = [('podiatry_state_name_unique', 'unique(name)', 'State name already exists')]
