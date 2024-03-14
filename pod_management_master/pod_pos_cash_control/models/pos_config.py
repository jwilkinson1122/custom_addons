# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    cash_control = fields.Boolean(string='Advanced Cash Control', compute='_compute_cash_control', default=False, help="Check the amount of the cashbox at opening and closing.")

    # pod_allow_cash_control = fields.Boolean(string="Enable Opening Closing Cash Control")
    # cash_control = fields.Boolean(string='Advanced Cash Control', compute='_compute_cash_control', help="Check the amount of the cashbox at opening and closing.")

    # @api.depends('payment_method_ids')
    # def _compute_cash_control(self):
    #     for config in self:
    #         config.cash_control = bool(config.payment_method_ids.filtered('is_cash_count'))


 

