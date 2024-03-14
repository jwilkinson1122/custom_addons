# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    batch_number = fields.Char(string='Batch Number', required=True, )
    mfg_date = fields.Date(string='Mfg. Date', required=True, )
    exp_date = fields.Date(string='Exp.date', required=True, )
    pack_size = fields.Char(string='Pack Size', required=True, )
    mrp = fields.Integer(string='MRP', required=True, )

