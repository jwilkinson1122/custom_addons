# -*- coding: utf-8 -*-
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    allow_measurements = fields.Boolean(string="Allow Measurements", config_parameter="pos_receipt_extend.allow_measurements")

