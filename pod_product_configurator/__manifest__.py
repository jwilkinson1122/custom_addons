# -*- coding: utf-8 -*-

{
    'name': "Sale Product Configurator",
    'version': '1.0',
    'category': 'Hidden',
    'summary': "Configure your products",
    'depends': ['sale'],
    'data': [
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'demo': [
        'data/sale_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_product_configurator/static/src/**/*',
        ],
    },
    'auto_install': True,
    'license': 'LGPL-3',
}
