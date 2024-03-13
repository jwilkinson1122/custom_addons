# -*- coding: utf-8 -*-

from odoo import fields, models


class OederType(models.Model):
    _name = 'pod.order.type'
    _description = 'Base order type'

    name = fields.Char(string='Name')
    img = fields.Image('Image', max_width=200, max_height=200)
    is_home_delivery = fields.Boolean('Is Home Delivery?')
