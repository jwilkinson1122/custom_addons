# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_device_route(models.Model):
    _name = 'podiatry.device.route'
    _description = 'Podiatry Device Route'

    name = fields.Char(string="Route", required=True)
    code = fields.Char(string="Code")
