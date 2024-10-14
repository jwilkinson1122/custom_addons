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

    # @api.constrains('is_clothing_size', 'is_textile_size')
    # def _assign_any_of_them_one(self):
    #     for res in self:
    #         if res.is_textile_size and res.is_clothing_size:
    #             raise ValidationError(_('Please Select Either Textile Sizing or Footwear Sizing'))

    @api.onchange('is_clothing_size')
    def apply_c_attributes(self):
        for rec in self:
            is_clothing_attribute = rec.attribute_line_ids.filtered(lambda m: m.attribute_id.is_clothing_size)
            lines = []
            if rec.is_clothing_size and not is_clothing_attribute:
                attribute_t = self.env['product.attribute'].search([('is_clothing_size', '=', True)])
                for attribute in attribute_t:
                    val = {
                        'attribute_id': attribute.id,
                        'value_ids': [(6, 0, attribute.value_ids.ids)],  # Properly add value_ids with a many2many command
                    }
                    lines.append((0, 0, val))
                rec.update({'attribute_line_ids': lines})
            elif not rec.is_clothing_size and is_clothing_attribute:
                # Remove the attribute if `is_clothing_size` is set to False
                rec.attribute_line_ids = [(2, line.id, 0) for line in is_clothing_attribute]

    @api.onchange('is_textile_size')
    def apply_t_attributes(self):
        for rec in self:
            is_textile_attribute = rec.attribute_line_ids.filtered(lambda m: m.attribute_id.is_textile_size)
            lines = []
            if rec.is_textile_size and not is_textile_attribute:
                attribute_t = self.env['product.attribute'].search([('is_textile_size', '=', True)])
                for attribute in attribute_t:
                    val = {
                        'attribute_id': attribute.id,
                        'value_ids': [(6, 0, attribute.value_ids.ids)],  # Properly add value_ids with a many2many command
                    }
                    lines.append((0, 0, val))
                rec.update({'attribute_line_ids': lines})
            elif not rec.is_textile_size and is_textile_attribute:
                # Remove the attribute if `is_textile_size` is set to False
                rec.attribute_line_ids = [(2, line.id, 0) for line in is_textile_attribute]
