# -*- coding: utf-8 -*-

{
    'name': "NWPL Prescription Product Configurator",
    "author": "NWPL",
    'version': '1.0',
    'category': 'Hidden',
    'summary': "Configure your products",

    'description': """
Technical module:
The main purpose is to override the prescription view to allow configuring products in the RX form.

It also enables the "optional products" feature.
    """,

    'depends': ['prescription'],
    'data': [
        'views/product_template_views.xml',
        'views/prescription_views.xml',
    ],
    'demo': [
        'data/prescription_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'prescription_product_configurator/static/src/**/*',
        ],
    },
    'auto_install': True,
    'license': 'LGPL-3',
}
