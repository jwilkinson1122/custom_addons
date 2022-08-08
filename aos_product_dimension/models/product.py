# -*- coding: utf-8 -*-
# import odoo.addons.decimal_precision as dp
# from odoo import api, fields, models, tools, _
# from odoo.modules import get_module_resource
# from odoo.osv.expression import get_unaccent_wrapper
# from odoo.exceptions import UserError, ValidationError
# from odoo.osv.orm import browse_record
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
import math
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

#import odoo.addons.decimal_precision as dp

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    #===========================================================================
    product_dimension = fields.Char('Dimension',help="Size Package Ex: 30x30x30")
    product_package_po = fields.Float('Quantity on Cartoon'  ,help="Qty in Package ext:10", digits='Product Unit of Measure')
    package_uom = fields.Many2one('product.packaging', help="Package ex:Dozen, Pack,", readonly=False)
    #package_uom = fields.Char('Package Name' ,default='Cartoon', help="Package ex:Dozen, Pack,", readonly=True)
    packaging_supp_yes  = fields.Boolean('yes')
    packaging_supp_no   = fields.Boolean('No')
    separator_x = fields.Char('X',default='x',related='product_variant_ids.separator_x')
    separator_x2 = fields.Char('X',default='x',related='product_variant_ids.separator_x2')
    packaging_weight = fields.Float('Packaging Weight')
    #height_dimension, length_dimension, width_dimension, weight_unit, size_unit, cubic_unit
    packaging_supp_quest = fields.Selection([('yes', 'Yes'),('no', 'No')],
        string='Standard Packaging', help='Do You Have Standard Packaging For This Product?',required=True, default='no') 
    #===========================================================================
    # COMPUTE ALL VARIANT PACKAGE
    #===========================================================================
    height_dimension = fields.Float('Dimension LxWxH (cm)', 
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    length_dimension = fields.Float('Length', 
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    width_dimension = fields.Float('Width', 
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    size = fields.Float('Volume Cartoon',digits=(10,4), 
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    volume_unit = fields.Float(
        string='Volume Unit', digits='Volume', help="The volume in m3.",
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    weight_unit = fields.Float(
        string='Weight Unit', digits='Stock Weight', help="The weight of the contents in Kg, not including any packaging, etc.",
        )
    volume = fields.Float(related='volume_unit',
        string='Volume', digits='Volume', help="The volume in m3.",
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
    weight = fields.Float(related='weight_unit',
        string='Weight', digits='Stock Weight', help="The weight of the contents in Kg, not including any packaging, etc.",
        )#compute='_compute_weight_unit', inverse='_set_weight_unit', store=True)
#     weight = fields.Float('Weight (Kg)', compute='_compute_weight_unit', digits='Stock Weight'),
#         inverse='_set_weight_unit', store=True)
#     volume = fields.Float('Volume',digits=(10,6), compute='_compute_weight_unit',
#         inverse='_set_weight_unit', store=True)   

    @api.onchange('package_uom')
    def _onchange_package_uom(self):
        if not self.package_uom:
            return
        #self.packaging_weight = self.package_uom.packaging_weight
        #self.product_package_po = self.package_uom.product_package_po
        self.length_dimension = self.package_uom.length
        self.height_dimension = self.package_uom.height
        self.width_dimension = self.package_uom.width
        self.weight = self.package_uom.max_weight
        self.weight_unit = self.package_uom.max_weight
        self.volume = self.package_uom.volume
        self.volume_unit = self.package_uom.volume
        #self.size = self.package_uom.size
        #return True
    
    
    @api.onchange('packaging_weight','product_package_po','height_dimension','length_dimension','width_dimension')
    def on_change_weight_package(self):
        if self.packaging_weight > 0 and  self.product_package_po > 0 :
            #BERAT PACKING / QUANTITY DALAM PACKING
            #self.weight = self.packaging_weight / self.product_package_po
            self.weight = round_down(self.packaging_weight / self.product_package_po, 3)
            self.weight_unit = round_down(self.packaging_weight / self.product_package_po, 3)
            #DIMENSI DALAM METER CUBIC  / QUANTITY DALAM PACKING
            self.volume = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)
            self.volume_unit = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)


    @api.onchange('height_dimension','length_dimension','width_dimension', 'product_package_po')
    @api.depends('height_dimension','length_dimension','width_dimension', 'product_package_po')
    def on_change_size_dimension(self):
        #DIMENSI DALAM M3
        self.size = (self.height_dimension * self.length_dimension * self.width_dimension) / 1000000
        #DIMENSI DALAM M3 / QUANTITY DALAM PACKING
        self.volume = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)
        self.volume_unit = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)
        #self.cubic_unit = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)

#             
#     
#     def confirm_product_template(self):
#         vals = {}
#         vals['state'] = 'confirmed'
#         
#         vals['packaging_supp_quest'] = self.packaging_supp_quest
#         vals['height_dimension'] = self.height_dimension
#         vals['length_dimension'] = self.length_dimension
#         vals['width_dimension'] = self.width_dimension
#         vals['package_uom'] = self.package_uom
#          
#         vals['product_package_po'] = self.product_package_po
#         vals['packaging_weight'] = self.packaging_weight
#         vals['weight'] = self.weight_unit
#         vals['volume'] = self.volume_unit
#         vals['size'] = self.size
#           
# #         vals['product_merk_id'] = self.product_merk_id and self.product_merk_id.id or False
# #         vals['product_type_id'] = self.product_type_id and self.product_type_id.id or False
# #         vals['product_brand_id'] = self.product_brand_id and self.product_brand_id.id or False
#         variants = self.env['product.product']
#         for variant in self.product_variant_ids:
#             variants += variant
#         variants.write(vals)
#         self.write({'state': 'confirmed'})
            
    
    
    def confirm_product_template(self):
        vals = super(ProductTemplate, self).confirm_product_template()
        vals['packaging_supp_quest'] = self.packaging_supp_quest
        vals['height_dimension'] = self.height_dimension
        vals['length_dimension'] = self.length_dimension
        vals['width_dimension'] = self.width_dimension
        vals['package_uom'] = self.package_uom and self.package_uom.id
         
        vals['product_package_po'] = self.product_package_po
        vals['packaging_weight'] = self.packaging_weight
        vals['weight'] = self.weight_unit
        vals['volume'] = self.volume_unit
        vals['size'] = self.size
        variants = self.env['product.product']
        for variant in self.product_variant_ids:
            variants += variant
        variants.write(vals)
        #print ('--confirm_product_template--',vals)
        return vals
            
    
    def draft_product_template(self):
        vals = super(ProductTemplate, self).draft_product_template()
        variants = self.env['product.product']
        for variant in self.product_variant_ids:
            variants += variant
        variants.write(vals)
        #print ('--draft_product_template--',vals)
        return vals
            
class ProductProduct(models.Model):
    _inherit='product.product'
    
    volume = fields.Float(digits='Volume')
    product_dimension = fields.Char('Dimension',help="Size Package Ex: 30x30x30")
    product_package_po = fields.Float('Quantity on Cartoon',help="Qty in Package ext:10")
    package_uom = fields.Many2one('product.packaging', help="Package ex:Dozen, Pack,", readonly=False)
    #package_uom = fields.Char('Package Name',default='Cartoon', help="Package ex:Dozen, Pack,", readonly=True)
    packaging_weight = fields.Float('Packaging Weight', digits='Stock Weight')
    height_dimension = fields.Float('Height', digits='Stock Dimension')
    length_dimension = fields.Float('Length', digits='Stock Dimension')
    width_dimension = fields.Float('Width', digits='Stock Dimension')
    separator_x = fields.Char('X',default='x',)
    separator_x2 = fields.Char('X',default='x',)
    packaging_supp_quest = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Standard Packaging', help='Do You Have Standard Packaging For This Product?',required=True, default='no' )
    packaging_supp_quest_dimension = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Standard Size', help='Do You Have Size This Product?'  ) 
    #weight_unit = fields.Float('Weight(Kg)', digits='Stock Weight')
    size = fields.Float('Volume Cartoon',digits=(10,4))
    #cubic_unit = fields.Float('Kubikasi Unit',digits=(10,6))
    
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        # TDE FIXME: strange
        if self._context.get('search_default_confirmed'):
            args += [('state', '=', 'confirmed')]
        return super(ProductProduct, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


#     @api.model
#     def create(self, vals):
#         if vals.get('product_tmpl_id',[]):
#             product_tmpl=self.env['product.template'].browse(vals['product_tmpl_id'])
#             vals['packaging_supp_quest'] = product_tmpl.packaging_supp_quest
#             vals['height_dimension'] = product_tmpl.height_dimension
#             vals['length_dimension'] = product_tmpl.length_dimension
#             vals['width_dimension'] = product_tmpl.width_dimension
#             vals['package_uom'] = product_tmpl.package_uom
#      
#             vals['product_package_po'] = product_tmpl.product_package_po
#             vals['packaging_weight'] = product_tmpl.packaging_weight
#             vals['weight'] = product_tmpl.weight
#             vals['volume'] = product_tmpl.volume
#             vals['size'] = product_tmpl.size
#              
#         return super(ProductProduct, self).create(vals)
    
#     @api.model
#     def name_search(self, name='', args=None, operator='ilike', limit=100):
#         if not args:
#             args = []
#         if name:
#             positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
#             products = self.env['product.product']
#             if operator in positive_operators:
#                 products = self.search([('default_code', '=', name)] + args, limit=limit)
#                 if not products:
#                     products = self.search([('barcode', '=', name)] + args, limit=limit)
#             if not products and operator not in expression.NEGATIVE_TERM_OPERATORS:
#                 # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
#                 # on a database with thousands of matching products, due to the huge merge+unique needed for the
#                 # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
#                 # Performing a quick memory merge of ids in Python will give much better performance
#                 products = self.search(args + [('default_code', operator, name)], limit=limit)
#                 if not limit or len(products) < limit:
#                     # we may underrun the limit because of dupes in the results, that's fine
#                     limit2 = (limit - len(products)) if limit else False
#                     products += self.search(args + [('name', operator, name), ('id', 'not in', products.ids)], limit=limit2)
#             elif not products and operator in expression.NEGATIVE_TERM_OPERATORS:
#                 products = self.search(args + ['&', ('default_code', operator, name), ('name', operator, name)], limit=limit)
#             if not products and operator in positive_operators:
#                 ptrn = re.compile('(\[(.*?)\])')
#                 res = ptrn.search(name)
#                 if res:
#                     products = self.search([('default_code', '=', res.group(2))] + args, limit=limit)
#             # still no results, partner in context: search on supplier info as last hope to find something
#             if not products and self._context.get('partner_id'):
#                 suppliers = self.env['product.supplierinfo'].search([
#                     ('name', '=', self._context.get('partner_id')),
#                     '|',
#                     ('product_code', operator, name),
#                     ('product_name', operator, name)])
#                 if suppliers:
#                     products = self.search([('product_tmpl_id.seller_ids', 'in', suppliers.ids)], limit=limit)
#             # type get on variant
#             #===================================================================
#             if not products:
#                 products = self.search([('attribute_value_ids.name', operator, name)], limit=limit)
#             #===================================================================
#         else:
#             products = self.search(args, limit=limit)
#         return products.name_get()

    @api.onchange('package_uom')
    def _onchange_package_uom(self):
        if not self.package_uom:
            return
        #print ('-_onchange_package_uom--',self.package_uom.length)
        #self.packaging_weight = self.package_uom.packaging_weight
        #self.product_package_po = self.package_uom.product_package_po
        self.length_dimension = self.package_uom.length
        self.height_dimension = self.package_uom.height
        self.width_dimension = self.package_uom.width
        self.weight = self.package_uom.max_weight
        self.weight_unit = self.package_uom.max_weight
        self.volume = self.package_uom.volume
        self.volume_unit = self.package_uom.volume
        #self.size = self.package_uom.size
        #return True
        
    @api.onchange('packaging_supp_quest', 'state')
    def onchange_packaging_supp_quest_prod(self):
        if self.packaging_supp_quest == 'no':
            self.length_dimension = 0
            self.height_dimension = 0
            self.width_dimension = 0
            self.package_uom = ''
            self.product_package_po = 0
            self.packaging_weight= 0

    @api.onchange('packaging_weight','product_package_po', 'state')
    def onchange_product_pack_id(self):
        if self.packaging_weight > 0 and  self.product_package_po > 0 :
            self.weight = self.packaging_weight / self.product_package_po
            self.volume = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)
            

    @api.onchange('height_dimension','length_dimension','width_dimension', 'state')
    def onchange_product_size(self):
        self.size = (self.height_dimension * self.length_dimension * self.width_dimension) / 1000000
        self.volume = ((self.height_dimension * self.length_dimension * self.width_dimension) / 1000000) / (self.product_package_po or 1)
            
#         
#     def confirm_product(self):
#         self.state = 'confirmed'
#         
#         
#     def draft_product(self):
#         self.state = 'draft'