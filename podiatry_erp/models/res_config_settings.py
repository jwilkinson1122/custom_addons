# -*- coding: utf-8 -*-
# Copyright 2020-now Al Hadi Tech - Pakistan
# License OPL-1

import base64
from odoo import models, fields, api, _

class InheritedResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pod_accommodation_chargeable = fields.Boolean(config_parameter='podiatry_erp.pod_accommodation')

    @api.model
    def get_values(self):
        res = super(InheritedResConfigSettings,self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        pod_accommodation_chargeable = params.get_param('pod_accommodation_chargeable')
        res.update(
            pod_accommodation_chargeable=pod_accommodation_chargeable,
        )
        return res


    def set_values(self):
        super(InheritedResConfigSettings,self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("pod_accommodation_chargeable",self.pod_accommodation_chargeable)


























