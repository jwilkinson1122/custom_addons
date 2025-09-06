import logging
import ast
import re
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class ProductAttributeSet(models.Model):
    _name = "product.attribute.set"
    _description = "Product Attribute Set"

    name = fields.Char(required=True, translate=True)
    attribute_ids = fields.Many2many(
        "product.attribute",
        "product_attribute_set_rel",
        "set_id",
        "attribute_id",
        string="Attributes",
    )
