# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_pos_opencashbox = fields.Boolean(string="Hide Opening Cash Control", default=True)
    # iface_tax_included = fields.Selection([('subtotal', 'Tax-Excluded Price'), ('total', 'Tax-Included Price')], string="Tax Display", default='subtotal', required=True)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hide_pos_opencashbox = fields.Boolean(related='pos_config_id.hide_pos_opencashbox',readonly=False)
    # pos_iface_tax_included = fields.Selection(related='pos_config_id.iface_tax_included', readonly=False)
