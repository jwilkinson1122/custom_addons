{
    "name": "Product Selection Wizard",
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
        # "data/product_category_data.xml",
        "data/product_section_configuration_data.xml",
        "views/product_selection_wizard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "product_selection_wizard/static/src/css/custom_statusbar.css",
            "product_selection_wizard/static/src/css/custom_tree_view.css",
        ],
    },
    "installable": True,
}
