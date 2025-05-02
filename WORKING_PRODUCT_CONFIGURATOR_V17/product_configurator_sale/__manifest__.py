{
    "name": "Product Configurator Sale",
    "version": "17.0.0.0.0",
    "category": "Generic Modules/Sale",
    "license": "AGPL-3",
    "depends": ["sale_management", "product_configurator", "stock"],
    "data": [
        "security/ir.model.access.csv",
        "data/menu_product.xml",
        "views/sale_view.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "auto_install": False,
}
