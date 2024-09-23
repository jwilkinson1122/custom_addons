# -*- coding: utf-8 -*-

from asyncio import constants
from cmath import cos
from odoo import models, fields, api, _

class PosCategoryInherit(models.Model):
    _inherit = "pos.category"

    pod_product_option_ids = fields.Many2many('product.product', string="Options", domain="[('available_in_pos', '=', True)]")
