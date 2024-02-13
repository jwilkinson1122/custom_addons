# -*- coding: utf-8 -*-

{
    'name': "NWPL - Prescription Product Configurator",
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'website': 'https://www.nwpodiatric.com',
    'category': 'Hidden',
    'summary': "Configure your products",
    'description': """Configure products in the Rx form.""",
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
