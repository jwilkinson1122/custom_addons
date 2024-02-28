# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DeviceCustomState(models.Model):
    _name = 'device.custom.state'
    _order = 'sequence asc'
    _description = 'Custom Status'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()

    _sql_constraints = [('device_state_name_unique', 'unique(name)', 'State name already exists')]
