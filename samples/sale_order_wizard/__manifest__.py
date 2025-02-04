{
    "name": "Sale Order Wizard",
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
        # "data/product_section_data.xml",
        "views/product_template_view.xml",
        "views/sale_order_section_views.xml",
        "views/sale_order_section_product_views.xml",
        "views/sale_order_wizard_views.xml",
        "views/sale_order_view.xml",
    ],
    "demo": [
        "demo/sale_order_wizard_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sale_order_wizard/static/src/css/custom_statusbar.css",
        ],
    },
    "installable": True,
}
