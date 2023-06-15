# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # reference = fields.Char(string='Practice Reference', required=True, copy=False, readonly=True,
    #                         default=lambda self: _('New'))
    customer_code = fields.Integer(string='Company code', required=True)
    next_code = fields.Integer(string='Next code')
