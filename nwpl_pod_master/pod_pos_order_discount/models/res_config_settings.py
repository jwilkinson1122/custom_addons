# -*- coding: utf-8 -*-


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_pod_allow_order_line_discount = fields.Boolean(
        related="pos_config_id.pod_allow_order_line_discount",
        string="Allow Line Discount",
        readonly=False,
    )
    pos_pod_allow_global_discount = fields.Boolean(
        related="pos_config_id.pod_allow_global_discount",
        string="Allow Global Discount",
        readonly=False,
    )
