# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_textile_size = fields.Boolean("Textile Sizing ?", default=False, store=True)
    is_clothing_size = fields.Boolean("Foot Ware Sizing ?", default=False, store=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_textile_size = fields.Boolean("Textile Sizing ?", default=False, store=True)
    is_clothing_size = fields.Boolean("Foot Ware Sizing ?", default=False, store=True)

    @api.constrains('is_clothing_size', 'is_textile_size')
    def _assign_any_of_them_one(self):
        for res in self:
            if res.is_textile_size and res.is_clothing_size:
                raise ValidationError(_('Please Select Anyone of Textile Sizing and Foot Ware Sizing '))

    @api.onchange('is_clothing_size')
    def apply_c_attributes(self):
        for rec in self:
            is_clothing_attribute = rec.attribute_line_ids.filtered(lambda m: m.attribute_id.is_clothing_size == True)
            lines = []
            if rec.is_clothing_size and not is_clothing_attribute:
                attribute_t = self.env['product.attribute'].search([('is_clothing_size', '=', True)])
                for line in attribute_t:
                    val = {
                        'attribute_id': attribute_t.id,
                        'value_ids': line.value_ids.ids,
                    }
                    lines.append((0, 0, val))
                rec.attribute_line_ids = lines
            else:
                if is_clothing_attribute:
                    for line in rec.attribute_line_ids:
                        if line.filtered(lambda m: m.attribute_id.is_clothing_size == True):
                            raise ValidationError(_('You Can Directly Remove Attributes from Line'))

    @api.onchange('is_textile_size')
    def apply_t_attributes(self):
        for rec in self:
            is_txt_attribute = rec.attribute_line_ids.filtered(lambda m: m.attribute_id.is_textile_size == True)
            lines = []
            if rec.is_textile_size and not is_txt_attribute:
                attribute_t = self.env['product.attribute'].search([('is_textile_size', '=', True)])
                for line in attribute_t:
                    val = {
                        'attribute_id': attribute_t.id,
                        'value_ids': line.value_ids.ids,
                    }
                    lines.append((0, 0, val))
                rec.attribute_line_ids = lines
            else:
                if is_txt_attribute:
                    for line in rec.attribute_line_ids:
                        if line.filtered(lambda m: m.attribute_id.is_textile_size == True):
                            if line.filtered(lambda m: m.attribute_id.is_textile_size == True):
                                raise ValidationError(_('You Can Directly Remove Attributes from Line'))