{
    "name": "NWPL - Product Attribute Preference",
    "summary": """Set product attribute preference per company""",
    "version": "17.0.0.0.0",
    "category": "Product",
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "license": "LGPL-3",
    "application": False,
    "depends": [
        "product",
        "stock",
    ],
    "excludes": [],
    "data": [
        "views/product_attribute_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "qweb": [],
    "post_init_hook": "initialize_attribute_is_preference_field",
}
