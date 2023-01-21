# -*- coding: utf-8 -*-
# License OPL-1

import base64
from odoo import models, fields, api, _


class InheritedResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    examination_chargeable = fields.Boolean(
        config_parameter='pod_erp.examination')

    @api.model
    def get_values(self):
        res = super(InheritedResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        examination_chargeable = params.get_param(
            'examination_chargeable')
        res.update(
            examination_chargeable=examination_chargeable,
        )
        return res

    def set_values(self):
        super(InheritedResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            "examination_chargeable", self.examination_chargeable)
