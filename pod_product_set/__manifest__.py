{
    "name": "NWPL - Product set",
    "category": "Sale",
    "license": "LGPL-3",
    "author": "NWPL",
    "version": "17.0.0.0.0",
    "website": "https://www.nwpodiatric.com",
    "depends": [
        "pod_prescription",
        "pod_prescription_management",
        "sale", 
        "sale_management", 
        "product"
        ],
    "data": [
        "security/ir.model.access.csv",
        "security/rule_product_set.xml",
        "views/product_set.xml",
        "views/product_set_line.xml",
        "wizard/product_set_add.xml",
        "views/sale_order.xml",
    ],
    "demo": ["demo/product_set.xml", "demo/product_set_line.xml"],
    "installable": True,
}
