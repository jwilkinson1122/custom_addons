# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_enable_cash_control = fields.Boolean(string="Enable Opening Closing Cash Control", default=False)




class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_enable_cash_control = fields.Boolean(string="Enable Opening Closing Cash Control", related="pos_config_id.pod_enable_cash_control", readonly=False)

