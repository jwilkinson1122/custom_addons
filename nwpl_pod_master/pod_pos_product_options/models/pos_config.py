# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    pod_enable_options = fields.Boolean(string="Enable Options")
    pod_add_options_on_click_product = fields.Boolean(string="Add Option when product add to cart")
    pod_allow_same_product_different_qty = fields.Boolean(string="Allow Same Product With Different Options")
