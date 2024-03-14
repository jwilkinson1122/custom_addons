# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.move"

    lice_number = fields.Char(related='partner_id.lice_number')


class AccountInvoice(models.Model):
    _inherit = "account.move.line"
    # _inherit = ['account.invoice.line', 'product.template']

    batch_number = fields.Char(related='product_id.batch_number')
    mfg_date = fields.Date(related='product_id.mfg_date')
    exp_date = fields.Date(related='product_id.exp_date')
    pack_size = fields.Char(related='product_id.pack_size')
    mrp = fields.Integer(related='product_id.mrp')
