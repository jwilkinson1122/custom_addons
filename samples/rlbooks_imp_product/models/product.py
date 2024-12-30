from odoo import api, fields, models


class ProductTemplateInherit(models.Model):    
    _inherit = 'product.template'

    followproduct_ids = fields.One2many('rlbooks.product.followproduct', 'main_product_id', 'Follow products')