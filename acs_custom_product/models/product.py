
from odoo import api, fields, models, tools, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    utility = fields.Float(string='Utilidad', compute="_compute_utility_product")
    unit_for_blister = fields.Float('Unidades x blister', compute="_compute_unit_for_blister")
    margin = fields.Float(string='Margen', compute="_compute_margin")


    @api.depends('utility')
    def _compute_margin(self):
        for rec in self:
            if rec.utility and rec.standard_price:
                rec.margin = rec.utility * 100 / rec.standard_price
            else:
                rec.margin = False
                
    def _compute_unit_for_blister(self):
        for product in self:
            product.unit_for_blister = 0.0
            if product.blister_for_box:
                product.unit_for_blister = product.unit_for_box / product.blister_for_box
            else:
                product.margin = False
                
    def _compute_utility_product(self):
        for product in self:
            product.utility = product.lst_price - product.standard_price

class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"
    
    price_x_1_18 = fields.Float('Precio con IGV', compute="_compute_price_x_1_18")

    def _compute_price_x_1_18(self):
        for rec in self:
            rec.price_x_1_18 = 0.0
            if rec.price:
                rec.price_x_1_18 = rec.price * 1.18