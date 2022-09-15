# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class podiatry_product_route(models.Model):
    _name = 'podiatry.product.route'
    _description = 'Medical Product Route'

    name = fields.Char(string="Route", required=True)
    code = fields.Char(string="Code")
