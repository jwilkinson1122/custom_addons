# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    delay_alert_prescription = fields.Integer(string='Delay alert prescription outdated', default=30, config_parameter='hr_prescription.delay_alert_prescription')
