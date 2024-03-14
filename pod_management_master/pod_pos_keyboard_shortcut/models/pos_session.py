# -*- coding: utf-8 -*-

from odoo import models

import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append("pod.keyboard.key.temp")
        result.append("pod.pos.keyboard.shortcut")
        return result

    def _get_pos_ui_pod_keyboard_key_temp(self, params):
        orders = self.env["pod.keyboard.key.temp"].search_read(**params["search_params"])
        return orders

    def _loader_params_pod_keyboard_key_temp(self):
        return {
            "search_params": {
                "domain": [],
                "fields": ["name", "pod_key_ids"],
            },
        }

    def _get_pos_ui_pod_pos_keyboard_shortcut(self, params):
        orders = self.env["pod.pos.keyboard.shortcut"].search_read(
            **params["search_params"]
        )
        return orders

    def _loader_params_pod_pos_keyboard_shortcut(self):
        return {
            "search_params": {
                "domain": [],
                "fields": [
                    "pod_key_ids",
                    "pod_shortcut_screen",
                    "config_id",
                    "payment_method_id",
                    "pod_payment_shortcut_screen_type",
                    "pod_shortcut_screen_type",
                ],
            },
        }
