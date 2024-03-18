# -*- coding: utf-8 -*-


from odoo import models, fields, api


class ResConfigSettiongsInhert(models.TransientModel):
    _inherit = "res.config.settings"

    pos_pod_enable_multi_barcode = fields.Boolean(
        related="pos_config_id.pod_enable_multi_barcode", readonly=False)
