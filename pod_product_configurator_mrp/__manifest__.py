
{
    "name": "Product Configurator Manufacturing",
    "version": "17.0.1.0.0",
    "category": "Manufacturing",
    "summary": "BOM Support for configurable products",
    "license": "AGPL-3",
    "depends": ["mrp", "pod_product_configurator"],
    "data": [
        "data/menu_product.xml",
        "views/mrp_view.xml",
        "security/configurator_security.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "/pod_product_configurator_mrp/static/src/js/list_controller.js",
            "/pod_product_configurator_mrp/static/src/js/kanban_controller.js",
            "/pod_product_configurator_mrp/static/src/js/form_controller.js",
            "/pod_product_configurator_mrp/static/src/scss/mrp_config.scss",
            "/pod_product_configurator_mrp/static/src/xml/mrp_production_views.xml",
        ],
    },
    "demo": ["demo/product_template.xml"],
    "qweb": ["static/src/xml/mrp_production_views.xml"],
    "installable": True,
    "auto_install": False,
}
