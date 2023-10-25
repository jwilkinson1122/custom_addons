#coding: utf-8

from odoo import fields, models


class product_template(models.Model):
    """
    Overwrite to add type
    """
    _inherit = "product.template"

    custom_type_id = fields.Many2one("template.custom.type", string="Custom Product Type")
