# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    is_device = fields.Boolean(string='Is Device')
    is_option = fields.Boolean(string='Is Option')
    
    uom_measure_type = fields.Selection(
        string="UoM Type of Measure",
        related="uom_id.measure_type",
        store=True,
        readonly=True,
    )
    
    @tools.ormcache()
    def _get_default_secondary_uom(self):
        return self.env.ref('uom.product_uom_dozen')


    secondary_uom_active = fields.Boolean(string='Secondary Unit ?', default=True)
    secondary_uom = fields.Many2one('uom.uom', 'Secondary Unit of Measure', 
        required=True, help="Default unit of measure used for all stock operations.",
        default=_get_default_secondary_uom)
    
    uom_name = fields.Char(string='Sec UoM Name', related='secondary_uom.name', readonly=True)
    on_hand_qty = fields.Float(
        'Quantity On Hand', compute='_compute_on_hand_qty',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")

    # def _compute_on_hand_qty(self):
    #     self.on_hand_qty = self.qty_available
    @api.depends('qty_available')
    def _compute_on_hand_qty(self):
        for record in self:
            if record.uom_id == record.secondary_uom:
                record.on_hand_qty = record.qty_available
            elif record.secondary_uom.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
                record.on_hand_qty = (record.uom_id.ratio / record.secondary_uom.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available

            elif record.secondary_uom.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (record.secondary_uom.ratio / record.uom_id.ratio) * record.qty_available 

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.secondary_uom.ratio * record.uom_id.ratio) * record.qty_available 
                
            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (1 / (record.secondary_uom.ratio * record.uom_id.ratio))* record.qty_available

            elif record.secondary_uom.uom_type == 'smaller' and record.uom_id.uom_type == 'smaller':
                record.on_hand_qty = (record.secondary_uom.ratio / record.uom_id.ratio) * record.qty_available
            
            elif record.secondary_uom.uom_type == 'bigger' and record.uom_id.uom_type == 'bigger':
                record.on_hand_qty = (record.uom_id.ratio / record.secondary_uom.ratio) * record.qty_available


# On Hand product
class ProductProduct(models.Model):
    _inherit = "product.product"

    product_secondary_uom_id = fields.Many2one('uom.uom', 'Secondary Unit of Measure', 
        related="product_tmpl_id.secondary_uom", domain="[('category_id', '=', product_sec_product_uom_category_id)]",
        help="Default unit of measure used for all stock operations.", readonly=False)
    product_sec_product_uom_qty = fields.Float(string='S-Qty on Hand', digits='Product Unit of Measure',
        compute="_compute_product_sec_product_uom_qty", store=True)    
    product_sec_product_uom_category_id = fields.Many2one(related='product_tmpl_id.secondary_uom.category_id', string="Sec Product Category")



    @api.depends('qty_available')
    def _compute_product_sec_product_uom_qty(self):
        for record in self:
            if record.uom_id == record.product_secondary_uom_id:
                record.product_sec_product_uom_qty = record.qty_available
            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available

            elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.qty_available 
                
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.qty_available 

            elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'smaller':
                record.product_sec_product_uom_qty = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.qty_available
            
            elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'bigger':
                record.product_sec_product_uom_qty = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.qty_available

    # @api.onchange('product_sec_product_uom_qty')
    # def _inverse_product_sec_product_uom_qty(self):
    #     for record in self:
    #         if record.uom_id == record.product_secondary_uom_id:
    #             record.qty_available = record.product_sec_product_uom_qty            
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (record.product_secondary_uom_id.ratio / record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'reference':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'reference':
    #              record.qty_available = (record.uom_id.ratio / record.product_secondary_uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'reference' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'smaller' and record.uom_id.uom_type == 'bigger':
    #             record.qty_available = (1 / (record.product_secondary_uom_id.ratio * record.uom_id.ratio))* record.product_sec_product_uom_qty
    #         elif record.product_secondary_uom_id.uom_type == 'bigger' and record.uom_id.uom_type == 'smaller':
    #             record.qty_available = (record.product_secondary_uom_id.ratio * record.uom_id.ratio) * record.product_sec_product_uom_qty
