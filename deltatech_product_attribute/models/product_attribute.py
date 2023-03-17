# ©  2008-2021 Deltatech
# See README.rst file on addons root folder for license details


import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ProductAttributeGroup(models.Model):
    _name = "product.attribute.group"
    _description = "Attribute Group"

    name = fields.Char()
    attribute_ids = fields.One2many("product.attribute", "group_id")
    type = fields.Selection([("single", "Single"), ("multiple", "Multiple")], default="single")
    min = fields.Integer()
    max = fields.Integer()


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    group_id = fields.Many2one("product.attribute.group")
    display_type = fields.Selection(selection_add=[("boolean", "Boolean")], ondelete={"boolean": "set default"})


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    bool_value = fields.Boolean(string="True Value")


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _get_combination_name(self):
        items = []
        for ptav in self._without_no_variant_attributes()._filter_single_value_lines():
            if ptav.attribute_id.display_type == "boolean":
                if ptav.product_attribute_value_id.bool_value:
                    items += [ptav.attribute_id.name]
            else:
                items += [ptav.name]

        return ", ".join(items)
