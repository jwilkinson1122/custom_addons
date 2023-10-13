from ast import literal_eval
import logging
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

# class ProductAttributeGroup(models.Model):
#     _name = "product.attribute.group"
#     _description = "Attribute Group"

#     name = fields.Char()
#     attribute_ids = fields.One2many("product.attribute", "group_id")
#     type = fields.Selection([("single", "Single"), ("multiple", "Multiple")], default="single")
#     min = fields.Integer()
#     max = fields.Integer()

class ProductAttributeCustomValue(models.Model):
    _inherit = 'product.attribute.custom.value'
    # _name = "product.attribute.custom.value"
    _description = 'Product Attribute Custom Value'
    # _order = 'custom_product_template_attribute_value_id, id'
    
    sale_order_line_id = fields.Many2one(
        'sale.order.line', 
        string="Sale Order Line", 
        required=True, 
        ondelete='cascade')

    _sql_constraints = [
        ('sol_custom_value_unique', 'unique(custom_product_template_attribute_value_id, sale_order_line_id)', "Only one Custom Value is allowed per Attribute Value per Order Line.")
    ]

    # name = fields.Char("Name", compute='_compute_name')
    # custom_product_template_attribute_value_id = fields.Many2one('product.template.attribute.value', string="Attribute Value", required=True, ondelete='restrict')
    # custom_value = fields.Char("Custom Value")

    # @api.depends('custom_product_template_attribute_value_id.name', 'custom_value')
    # def _compute_name(self):
    #     for record in self:
    #         name = (record.custom_value or '').strip()
    #         if record.custom_product_template_attribute_value_id.display_name:
    #             name = "%s: %s" % (record.custom_product_template_attribute_value_id.display_name, name)
    #         record.name = name

