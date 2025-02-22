# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductLabelLines(models.TransientModel):
    _name = 'print.product.label.lines'
    _description = 'Product Label Lines'
    _order = 'sequence'

    sequence = fields.Integer(default=900)