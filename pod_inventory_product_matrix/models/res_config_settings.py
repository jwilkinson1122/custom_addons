# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inventory_product_matrix = fields.Boolean(string="Inventory Grid Entry")

    @api.onchange('group_product_variant')
    def _onchange_group_product_variant(self):
        # super(ResConfigSettings,self)._onchange_group_product_variant()
        """The product Configurator requires the product variants activated.
        If the user disables the product variants -> disable the product configurator as well"""
        if self.inventory_product_matrix and not self.group_product_variant:
            self.inventory_product_matrix = False
