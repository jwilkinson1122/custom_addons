# -*- coding: utf-8 -*-

from odoo import fields, models


class custom_template_field(models.Model):
    _name = 'custom.template.field'
    _inherit = ["custom.extra.field"]
    _description = 'Custom Template Field'
    _field_code = "tmpl"
    _linked_model = "product.template"
    _type_field = "custom_type_id"
    _type_field_model = "template.custom.type"
    _backend_views = ["product_custom_fields.product_template_view_form"]

    types_ids = fields.Many2many(
        "template.custom.type",
        "template_custom_type_custom_template_field_reltable",
        "template_custom_type_rel_id",
        "custom_template_field_rel_id",
        string="Types",
        help="Leave it empty, if this field should appear for all templates disregarding type"
    )
    placement = fields.Selection(
        selection_add=[
            ("left_panel_group", "Left Column"),
            ("right_panel_group", "Rigth Column"),
            ("after_description_group", "After Internal Notes"),
        ]
    )
    sel_options_ids = fields.One2many(context={'default_model': "custom.template.field"},)
