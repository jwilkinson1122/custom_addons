# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _


class InheritedResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    service_chargeable = fields.Boolean(
        config_parameter='pod_erp.test_charge')

    @api.model
    def get_values(self):
        res = super(InheritedResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        service_chargeable = params.get_param(
            'service_chargeable')
        res.update(
            service_chargeable=service_chargeable,
        )
        return res

    def set_values(self):
        super(InheritedResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "service_chargeable", self.service_chargeable)
