# -*- coding: utf-8 -*-

from odoo import fields, models


class res_config_settings(models.TransientModel):
    """
    Overwrite to optionally hide/show custom product types
    """
    _inherit = "res.config.settings"

    group_custom_fields_products_show_type = fields.Boolean(
        "Show custom product types", 
        implied_group="product_custom_fields.group_custom_fields_products_show_type",
    )