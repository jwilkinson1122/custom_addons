# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_drug_route(models.Model):
    _name = 'podiatry.drug.route'
    _description = 'Podiatry Drug Route'

    name = fields.Char(string="Route", required=True)
    code = fields.Char(string="Code")
