# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    """ Inheriting 'product.template' for adding custom field and functionality.
    """
    _inherit = 'product.template'

    to_make_mrp = fields.Boolean(
        string='To Create MRP Order',
        help="Check if the product should make mrp order")

    @api.onchange('to_make_mrp')
    def onchange_to_make_mrp(self):
        """ Raise validation error if bom is not set in 'product.template'."""
        if self.to_make_mrp:
            if not self.bom_count:
                raise ValidationError(_(
                    'Please set Bill of Material for this product.'))
