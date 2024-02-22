{
    "name": "NWPL - Product Info for Customer Sale",
    "version": "17.0.0.0.0",
    "summary": "Loads in every sale/prescription order line the customer code defined "
    "in the product",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Prescriptions/Sales",
    "license": "LGPL-3",
    "depends": [
        "sale", 
        "pod_prescription",
        "pod_product_info_for_customer"
        ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_customerinfo_views.xml",
        "views/prescription_order_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
}
