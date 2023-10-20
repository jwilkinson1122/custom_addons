# -*- coding: utf-8 -*-

from odoo import models, api, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        if self.env.user.has_group('pod_manager.group_pod_user'):
            res.append(self.env.ref('pod_manager.menu_pod_practitioner').id)
        return res
