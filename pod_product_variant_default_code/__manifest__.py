{
    "name": "NWPL - Product Variant Default Code",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3",
    "category": "Product",
    "depends": ["product"],
    "data": [
        "security/product_security.xml",
        "data/ir_config_parameter.xml",
        "views/product_attribute_view.xml",
        "views/product_view.xml",
        "views/config_settings_view.xml",
    ],
    "demo": ["demo/attribute_demo.xml"],
    "installable": True,
}
