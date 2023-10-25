#coding: utf-8

from odoo import fields, models


class template_custom_type(models.Model):
    """
    The model to classify template by types (for custom fields attributes)
    """
    _inherit = "custom.field.type"
    _name = "template.custom.type"
    _description = "Template Type"
    _custom_field_models = ["custom.template.field"]

    custom_fields_ids = fields.Many2many(
        "custom.template.field",
        "template_custom_type_custom_template_field_reltable",
        "custom_template_field_rel_id",
        "template_custom_type_rel_id",
        string="Custom Template Fields",
    )
