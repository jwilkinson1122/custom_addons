# -*- coding: utf-8 -*-
# Part of Northwest Podiatric Laboratory. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class device_route(models.Model):
    _name = 'podiatry.device.route'
    _description = 'Podiatry Device Route'

    name = fields.Char(string="Route",required=True)
    code = fields.Char(string="Code")

