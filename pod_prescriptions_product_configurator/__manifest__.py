# -*- coding: utf-8 -*-

{
    'name': "NWPL Prescription Product Configurator",
    "author": "NWPL",
    'version': '1.0',
    'category': 'Hidden',
    'summary': "Configure your products",

    'description': """
Technical module:
The main purpose is to override the prescriptions_order view to allow configuring products in the SO form.

It also enables the "optional products" feature.
    """,

    'depends': ['pod_prescriptions'],
    'data': [
        'views/product_template_views.xml',
        'views/prescriptions_order_views.xml',
    ],
    'demo': [
        'data/prescriptions_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_prescriptions_product_configurator/static/src/**/*',
        ],
    },
    'auto_install': True,
    'license': 'LGPL-3',
}
