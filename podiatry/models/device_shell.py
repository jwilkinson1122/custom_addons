# -*- coding: utf-8 -*-

from odoo import models, fields


class DeviceShell(models.Model):
    _name = 'device.shell'
    _description = 'Shell / Foundation'
    _rec_name = 'device_foundation'

    device_foundation = fields.Char('Device Shell/Foundation', required=True)
    collection = fields.Char('Collection')
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id
                                  .currency_id.id,
                                  required=True)
    price = fields.Monetary(string='Price')
