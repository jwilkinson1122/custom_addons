{
    "name": "NWPL - Product Info for Customers",
    "summary": "Allows to define prices for customers in the products",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "category": "Prescriptions/Sales",
    "license": "LGPL-3",
    "depends": ["product"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
    ],
    "demo": ["demo/product_demo.xml"],
    "installable": True,
}
