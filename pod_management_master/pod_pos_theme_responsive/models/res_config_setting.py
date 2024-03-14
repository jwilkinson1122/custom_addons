# -*- coding: utf-8 -*-


from odoo import  fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pod_pos_night_mode = fields.Boolean(related='pos_config_id.pod_pos_night_mode', readonly=False)
   