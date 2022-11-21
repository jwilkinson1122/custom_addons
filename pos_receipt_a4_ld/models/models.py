# -*- coding: utf-8 -*-
# Part of Lebowski. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.onchange('use_a4_receipt')
    def _onchange_use_a4_receipt(self):
        if not self.use_a4_receipt:
            self.use_a4_receipt_as_default = False
            self.tracking = False

    use_a4_receipt = fields.Boolean("Use A4 Receipt?", default=True)
    use_a4_receipt_as_default = fields.Boolean("Use A4 Receipt as default?")
    tracking = fields.Selection([('barcode', 'Barcode'), ('qrcode', 'Qrcode')], string="Tracking", default='barcode')
    show_taxes = fields.Boolean("Show Taxes?", default=True)
