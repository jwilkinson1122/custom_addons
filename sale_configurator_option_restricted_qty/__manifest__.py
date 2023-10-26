{
    "name": "Sale Configurator Option Restricted Qty",
    "summary": "Manage Restricted Qty on Sale configurator",
    "version": "15.0.1.0.0",
    "category": "Sale",
    "website": "https://nwpodiatric.com",
    "author": " NWPL",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["sale_configurator_option", "sale_restricted_qty"],
    "data": [
        "views/product_configurator_option_view.xml",
        "views/sale_view.xml",
    ],
    # "demo": ["demo/product_demo.xml", "demo/sale_demo.xml"],
    "qweb": [],
}
