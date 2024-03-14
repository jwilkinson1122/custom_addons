# -*- coding: utf-8 -*-


from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_pos_night_mode = fields.Boolean(string="Enable Night Mode")
