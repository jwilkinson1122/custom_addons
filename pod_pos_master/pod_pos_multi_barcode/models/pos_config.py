# -*- coding: utf-8 -*-


from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    pod_enable_multi_barcode = fields.Boolean(string="Enable Multi Barcode")
