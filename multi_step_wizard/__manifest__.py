{
    "name": "Multi-Steps Wizards",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base", "contacts", "sale", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "views/multi_step_wizard_views.xml",
        "wizards/sale_order_wizard.xml",
        "views/sale_order_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # "multi_step_wizard/static/src/js/close_wizard_refresh_view.esm.js",
        ],
    },
    "installable": True,
}
