# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_quantity_unit(models.Model):
    _name = 'podiatry.quantity.unit'
    _description = 'Podiatry Quantity Unit'

    name = fields.Char(string="Unit", required=True)
    description = fields.Char(string="Description")
