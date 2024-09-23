# -*- coding: utf-8 -*-
from odoo import models, fields

class PosConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_pod_enable_order_reprint = fields.Boolean(related="pos_config_id.pod_enable_order_reprint", readonly=False)
    pos_pod_enable_re_order = fields.Boolean(related="pos_config_id.pod_enable_re_order", readonly=False)
    pos_pod_enable_order_list = fields.Boolean(related="pos_config_id.pod_enable_order_list", readonly=False)
    pos_pod_load_order_by = fields.Selection(related="pos_config_id.pod_load_order_by", readonly=False)
    pos_pod_session_wise_option = fields.Selection(related="pos_config_id.pod_session_wise_option", readonly=False)
    pos_pod_day_wise_option = fields.Selection(related="pos_config_id.pod_day_wise_option", readonly=False)
    pos_pod_last_no_days = fields.Integer(related="pos_config_id.pod_last_no_days", readonly=False)
    pos_pod_last_no_session = fields.Integer(related="pos_config_id.pod_last_no_session", readonly=False)
    pos_pod_how_many_order_per_page = fields.Integer(related="pos_config_id.pod_how_many_order_per_page", readonly=False)

   
    
