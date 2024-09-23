# -*- coding: utf-8 -*-
 
from odoo import fields, models

class PodPosConfig(models.Model):
    _inherit = 'pos.config'

    pod_pos_night_mode = fields.Boolean(string="Enable Night Mode")
    add_menu_bar = fields.Boolean('Add a Menu Bar', default=True)