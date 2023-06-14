# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    customer_code = fields.Integer(string='Company code', required=True)
    next_code = fields.Integer(string='Next code')
