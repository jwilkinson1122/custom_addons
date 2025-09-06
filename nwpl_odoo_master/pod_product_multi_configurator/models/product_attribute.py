import logging
import ast
import re
from lxml import etree
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    _order = "sequence"
    
    attribute_group_id = fields.Many2one(
        "product.attribute.group",
        string="Configurator Group",
        help="Groups attributes together in the product configurator UI.",
    )

    sequence_group = fields.Integer(
        related="attribute_group_id.sequence",
        store=True,
        help="Sequence of the group (for sorting in the configurator).",
    )

    def copy(self, default=None):
        """Add ' (Copy)' in name to prevent attribute
        having same name while copying"""
        if not default:
            default = {}
        new_attrs = self.env["product.attribute"]
        for attr in self:
            default.update({"name": attr.name + " (copy)"})
            new_attrs += super(ProductAttribute, attr).copy(default)
        return new_attrs


   