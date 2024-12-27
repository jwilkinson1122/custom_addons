{
    "name": "Multi-Steps Wizards",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "contacts", "sale", "sale_management", "product"],
    "data": [
        "security/ir.model.access.csv",
        "report/sale_order_templates.xml",
        "views/multi_step_wizard_views.xml",
        # "wizards/sale_order_wizard.xml",
        "views/sale_order_views.xml",
        "wizards/sale_order_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "multi_step_wizard/static/src/js/section_wise_subtotal.js",
        ],
    },
    "installable": True,
}
