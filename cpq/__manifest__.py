{
    "name": "CPQ",
    "summary": "Dynamic Configure-Price-Quote-style generation of products",
    "author": "NWPL",
    "category": "Sales/Sales",
    "version": "17.0.1.0.0",
        "depends": ["product", "sale_stock"],
    # "depends": ["product", "web", "sale", "stock", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/product_product.xml",
        "views/product_attribute.xml",
        "views/product_options.xml",
        "views/menu.xml",
    ],
    "demo": [],
    "license": "LGPL-3",
    "assets": {
        "web.assets_backend": [
            "cpq/static/src/components/**/*",
        ],
    },
}
