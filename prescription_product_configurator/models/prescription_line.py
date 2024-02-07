# -*- coding: utf-8 -*-


from odoo import fields, models


class PrescriptionLine(models.Model):
    _inherit = 'prescription.line'

    is_configurable_product = fields.Boolean(
        string="Is the product configurable?",
        related='product_template_id.has_configurable_attributes',
        depends=['product_id'])
    
    product_template_attribute_value_ids = fields.Many2many(
        related='product_id.product_template_attribute_value_ids',
        depends=['product_id'])
