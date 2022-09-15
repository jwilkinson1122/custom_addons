# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_device_quantity(models.Model):
    _name = 'podiatry.device.quantity'
    _description = 'podiatry device quantity'

    name = fields.Char(string="Frequency", required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")
