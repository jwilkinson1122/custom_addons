{
    "name": "Multi-Steps Wizards",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "base",
        "base_setup",
        "contacts",
        "sale",
        "sale_management",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/multi_step_wizard_sections_data.xml",
        "data/wizard_section_configuration_data.xml",
        "views/wizard_section_configuration_views.xml",
        "views/multi_step_wizard_views.xml",
        "views/product_views.xml",
        "views/sale_order_wizard.xml",
        "views/sale_order_views.xml",
        # "report/sale_order_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "multi_step_wizard/static/src/js/sale_order_wizard_form_renderer.js",
            # "multi_step_wizard/static/src/js/section_wise_subtotal.js",
        ],
    },
    "installable": True,
}
