# -*- coding: utf-8 -*-
from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    pod_multi_barcode_unique = fields.Boolean('Is Multi Barcode Unique ?')

class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    pod_multi_barcode_unique = fields.Boolean(string="Is Multi Barcode Unique ?",related='company_id.pod_multi_barcode_unique',readonly=False)
