# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    product_id = fields.Many2one('product.product', string='product', domain=[('product_classify', '!=', 'product')], change_default=True,ondelete='restrict')
    product_qty = fields.Float('quantity',digits='Product Unit of Measure')
    product_uom = fields.Many2one('uom.uom', string='unit of measure',readonly=True,related='product_id.uom_id')

    @api.onchange('product_id')
    def get_default_name(self):
        if self.product_id:
            self.name = self.product_id.display_name


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    product_id = fields.Many2one('product.product', string='product', related='product_attribute_value_id.product_id', store=True, change_default=True,ondelete='restrict', readonly=True)
    product_qty = fields.Float('quantity',digits='Product Unit of Measure', related='product_attribute_value_id.product_qty', store=True, readonly=True)
    product_uom = fields.Many2one('uom.uom', string='unit of measure', readonly=True, related='product_id.uom_id')
