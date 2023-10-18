from odoo import api, fields, models

class ProductConfigLine(models.Model):
    _inherit = "product.config.line"
    _description = "Product Config Line"
    
    
class ProductConfigSession(models.Model):
    _inherit = "product.config.session"
    _description = "Product Config Session"
    

class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    laterality = fields.Selection([
        ('lt_single', 'Left'),
        ('rt_single', 'Right'),
        ('bl_pair', 'Bilateral')
    ], string='Laterality', default='bl_pair')
    
    value_left = fields.Char(string='Value Left')  # New field for left foot value
    value_right = fields.Char(string='Value Right')  # New field for right foot value

class ProductConfigStepLine(models.Model):
    _inherit = "product.config.step.line"

    laterality = fields.Selection([
        ('lt_single', 'Left'),
        ('rt_single', 'Right'),
        ('bl_pair', 'Bilateral')
    ], string='Laterality', default='bl_pair')
