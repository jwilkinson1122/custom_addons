# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_enable_cash_in_out_statement = fields.Boolean("Enable Cash In/Out Statement")
    pod_enable_payment = fields.Boolean(string="Enable Payment Detail")
    # pod_enable_cash_control = fields.Boolean(string="Enable Opening Closing Cash Control")
