# -*- coding: utf-8 -*-

{
    "name": "Product Options",
    "summary": """Odoo Product Options facilitates you to set manage variants for your products without making their variants through product options.""",
    "category": "Sales",
    "version": "1.0",
    "sequence": "1",
    "description": """Manage product options""",
    "depends": ["base", "product", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        # "data/product_options_data.xml",
        "views/product_options_views.xml",
        "views/product_template_views.xml",
        "views/sale_views.xml",
        "wizard/option_selection_wizard_views.xml",
    ],
    # "demo": ["data/product_options_demo.xml"],
    "application": True,
}
