import logging
import ast
import re
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class ProductAttributeGroup(models.Model):
    _name = "product.attribute.group"
    _description = "Attribute Group"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
