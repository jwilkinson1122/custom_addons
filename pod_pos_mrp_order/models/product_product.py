# -*- coding: utf-8 -*-
from odoo import api, models, _


class ProductProduct(models.Model):
    """ Inheriting 'product.product' for adding custom functionality."""
    _inherit = 'product.product'

    @api.onchange('to_make_mrp')
    def onchange_to_make_mrp(self):
        """ Raise validation error if bom is not set in 'product.product'."""
        if self.to_make_mrp:
            if not self.bom_count:
                raise Warning(
                    _('Please set Bill of Material for this product.'))
