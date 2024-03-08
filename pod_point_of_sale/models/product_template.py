# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_make_mrp = fields.Boolean(string='To Create MRP Order', help="Check if the product should make mrp order")
    bom_product = fields.Boolean(string='POS BOM Product')
    modifier_ok = fields.Boolean(string='Modifier Product')
    device_laterality = fields.Boolean(string='Display Device Laterlity?')
    modifier_groups_ids = fields.Many2many("modifier.product", string="Modifier Groups")
    sub_products_ids = fields.Many2many("product.product", string="Sub Products")
    modifier_attribute_product_id = fields.One2many('modifier.attribute','product_temp_id', string='Modifier Attribute')
    
    @api.onchange('to_make_mrp')
    def onchange_to_make_mrp(self):
        if self.to_make_mrp:
            if not self.bom_count:
                raise ValidationError(_('Please set Bill of Material for this product.'))
    
    def get_modifiers(self):
        modifierAttribute = self.env['modifier.attribute']
        modifier_group = self.modifier_groups_ids
        for modifier in modifier_group:
            for product in modifier.modifier_product_id:
                for attr in product.with_prefetch().product_variant_ids:
                    product_record = self.env['product.product'].browse(attr.id) 
                    name = product_record.display_name
                    output = name[name.find("(")+1:name.rfind(")")]
                    
                    vals = {
                        'product_id':attr.id,
                        'product_temp_id': self.id,
                        'price':attr.lst_price,
                        'display_name':output
                    }
                    is_exist = modifierAttribute.search([('product_id', '=', vals['product_id'])])
                    if is_exist:
                        pass
                    else:
                        modifierAttributeRecord = modifierAttribute.create(vals)

    

            