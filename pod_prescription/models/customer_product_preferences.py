from odoo import models, fields

class CustomerProductPreference(models.Model):
    _name = 'customer.product.preference'
    _description = 'Customer Product Preferences'

    customer_id = fields.Many2one('res.partner', string='Customer')
    
    product_template_id = fields.Many2one('product.template', string='Product Template')
    
    preference_type = fields.Selection([
        ('arch_height', 'Arch Height'),
        # Add other preference types here
    ], string='Preference Type')
    
    preference_value = fields.Selection([
        ('very_high', 'Very High'),
        ('high', 'High'),
        ('standard', 'Standard'),
        ('low', 'Low'),
        # Define other values here
    ], string='Preference Value')
