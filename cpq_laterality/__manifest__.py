{
    "name": "cpq_laterality",
    "summary": "Laterality/Fabric Custom Values",
    "author": "NWPL",
    "category": "Sales",
    "version": "17.0.1.0.0",
    "license": "LGPL-3",
    "depends": [
        "sale_stock",
        "cpq",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_attribute.xml",
        "views/product_laterality.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cpq_laterality/static/src/components/*.xml",
        ],
    },
}
