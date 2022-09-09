# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_device_dosage(models.Model):
    _name = 'podiatry.device.dosage'
    _description = 'podiatry device dosage'

    name = fields.Char(string="Frequency", required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")
