# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Product Configurator',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'version': '17.0.0.0.0',
    'category': 'Hidden',
    'summary': 'Configure your products',
    'description': """ Allow configuring products in the prescription form. It also enables the "optional products" feature.""",
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
