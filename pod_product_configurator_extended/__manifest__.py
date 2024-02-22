
{
    "name": "NWPL - Extend Product Configurator",
    "version": "17.0.0.0.0",
    "summary": "Enhance the product configurator",
    "description": "Enhance the product configurator",
    "category": "Products",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "sale_product_configurator",
    ],
    "data": [
        "views/product_attribute_views.xml",
        "data/product_attributes.xml",
    ],
    'assets': {
        'web.assets_backend': [
            # 'sale_product_configurator_extended/static/src/**/*',

        ]
    },
    "installable": True,
    "auto_install": False,
}
