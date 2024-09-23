# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_enable_cash_in_out_statement = fields.Boolean(related="pos_config_id.pod_enable_cash_in_out_statement", readonly=False)
    pos_pod_enable_payment = fields.Boolean(related="pos_config_id.pod_enable_payment", readonly=False)
    # pos_pod_enable_cash_control = fields.Boolean(string="Enable Opening Closing Cash Control", related="pos_config_id.pod_enable_cash_control", readonly=False)
