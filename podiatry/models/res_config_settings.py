# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    delay_alert_prescription = fields.Integer(string='Delay alert prescription outdated', default=30, config_parameter='hr_podiatry.delay_alert_prescription')
