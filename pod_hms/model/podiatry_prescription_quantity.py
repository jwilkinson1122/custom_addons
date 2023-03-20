# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_prescription_quantity(models.Model):
    _name = 'podiatry.prescription.quantity'
    _description = 'podiatry prescription quantity'

    name = fields.Char(string="Frequency", required=True)
    abbreviation = fields.Char(string="Abbreviation")
    code = fields.Char(string="Code")
