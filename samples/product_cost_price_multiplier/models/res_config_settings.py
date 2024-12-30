from odoo import models, fields, api

        
class ResConfigSalesRate(models.Model):
    _name = 'res.config.sales.rate'
    _description = 'Configuration Sales Rate'
    
    rate = fields.Float(string="Rate")
    maxvalue = fields.Float(string="Maximum Value")
    category_id = fields.Many2one('product.category', string="Category", ondelete='cascade')
    
    

class ProductCategory(models.Model):
    _inherit = 'product.category'

    default_rate = fields.Float(string="Default Max Rate")
    sales_rate_ids = fields.One2many('res.config.sales.rate', 'category_id', string="Sales Rates")
    
    def call_update_product_prices_cron(self):
        self.env['product.price.updater'].update_product_prices_cron()     