from odoo import models, fields
import logging

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    price_locked = fields.Boolean(string="Price Locked", default=False)
    price_custom_rate = fields.Float(string="Custom Price Rate",  digits=(4, 2),  default=False)


class ProductPriceUpdater(models.Model):
    _name = 'product.price.updater'
    _description = 'Product Price Updater'

    def _update_product_prices(self):
    
        _logger = logging.getLogger(__name__)
        
        unlocked_products = self.env['product.product'].search([ ('price_locked', '=', False), ('standard_price', '>', 0), ('sale_ok', '=', True) ])
        
       
        _logger = logging.getLogger(__name__)

        for product in unlocked_products:
            custom_rate = product.price_custom_rate
            new_price = product.standard_price
            if custom_rate > 0:
                new_price = product.standard_price * custom_rate
            else:
                product_category = product.categ_id
                while product_category:
                    _logger.debug('PRODUCT NAME: ' +  product.name + " FIRST - CATEGORY -> " + str(product_category.name))
                    if product_category.default_rate > 0:
                        _logger.debug('PRODUCT NAME: ' + product.name + " VALID CAT " + str(product_category.name) + " Rate -> " + str(product_category.default_rate))
                    
                        minvalue = 0
                        for record in sorted(product_category.sales_rate_ids, key=lambda x: x.maxvalue):
                            rate = record.rate
                            maxvalue = record.maxvalue
                            if product.standard_price > minvalue and product.standard_price <= maxvalue:
                                
                                new_price = product.standard_price * rate
                                _logger.debug('PRODUCT NAME: ' +  product.name + " STANDARD PRICE "+ str(product.standard_price) + " RATE " + str(rate) + " NEW PRICE " + str(new_price))
                            
                            minvalue = maxvalue
                            
                        if product.standard_price > minvalue:
                            new_price = product.standard_price * product_category.default_rate
                        
                        product_category = ''
                    
                    else:           
                        _logger.debug('PRODUCT NAME: ' +  product.name + " ELSE - CATEGORY -> " + str(product_category.name))
                        product_category = product_category.parent_id  # Move to the parent category
                    
                    
            _logger.debug('PRODUCT NAME: ' + product.name + " NEW PRICE -> "+ str(new_price)) 
                
            product.write({'list_price': new_price})

    def update_product_prices_cron(self):
        self._update_product_prices()
        return True
        
