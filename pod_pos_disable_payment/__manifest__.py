# -*- coding: utf-8 -*-
{
    'name': 'NWPL - Disable payments in POS',
    'version': '17.0.0.0.0',
    'license': 'LGPL-3',
    'author': 'NWPL',
    'category': 'Point of Sale',
    'summary': 'Control access to the POS payments',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'pod_point_of_sale',
        ],
    'data': [
        'views/views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_pos_disable_payment/static/src/css/pos.css',
            'pod_pos_disable_payment/static/src/js/tour.js',
        ],
        'point_of_sale.assets': [
            'pod_pos_disable_payment/static/src/js/pos_disable_payment.js',
        ]
    },
    'demo': [
    ],
    'assets': {
        'web.assets_tests': [
            'pod_pos_disable_payment/tests/test_default.py',
        ],
    },

    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
}
