# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pod_pos_enable_shortcut = fields.Boolean(
        related="pos_config_id.pod_enable_shortcut",
        string="Enable Shortcut Key",
        readonly=False,
    )
    pod_pos_shortcut_keys_screen = fields.One2many(
        related="pos_config_id.pod_shortcut_keys_screen",
        string="POS Shortcut Key",
        readonly=False,
    )
    pod_pos_payment_shortcut_keys_screen = fields.One2many(
        related="pos_config_id.pod_payment_shortcut_keys_screen",
        string="POS Payment Method Shortcut Key",
        readonly=False,
    )
