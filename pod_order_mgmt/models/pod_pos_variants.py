# -*- coding: utf-8 -*-

from odoo import api, models, fields


class PosVarients(models.Model):

    _inherit = ['product.template']

    pos_variants = fields.Boolean('pos variants', default=False)
    variant_line_ids = fields.One2many(
        'variants.tree', 'variants_id', string="Configure Variants")


class VariantsSelection(models.Model):

    _name = 'variants.tree'

    variants_id = fields.Many2one('product.template')
    attribute = fields.Many2one(
        'product.attribute', string='Attribute', ondelete='restrict', required=True, index=True)
    value = fields.Many2many('product.attribute.value', string='Values')
    extra_price = fields.Char(string="Price Extra")
    pos_active = fields.Boolean(string="Active")
