
{
    "name": "Product Configurator",
    "version": "17.0.0.0.0",
    "summary": "Enhance the product configurator",
    "description": "Sale module",
    "category": "Other",
    "author": "Niboo SRL",
    "website": "https://niboo.com",
    "license": "Other proprietary",
    "depends": [
        "sale_product_configurator",
    ],
    "data": [
        "views/product_attribute_views.xml",
        "data/product_attributes.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sale_product_configurator_extended/static/src/**/*',

        ]
    },
    "installable": True,
    "auto_install": False,
}
