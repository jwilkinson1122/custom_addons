{
    "name": "NWPL - Order Product Set",
    "category": "Prescriptions/Sales",
    "license": "LGPL-3",
    "author": "NWPL",
    "version": "17.0.0.0.0",
    "website": "https://www.nwpodiatric.com",
    "depends": [
        "pod_prescription", 
        "pod_prescription_management", 
        "sale", 
        "sale_management", 
        "pod_product_set",
        ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_set.xml",
        "views/product_set_line.xml",
        "wizard/product_set_add.xml",
        "views/sale_order.xml",
    ],
    "demo": ["demo/product_set_line.xml"],
    "installable": True,
}
