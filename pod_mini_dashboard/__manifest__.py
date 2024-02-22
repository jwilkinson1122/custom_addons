# -*- coding: utf-8 -*-
{
    'name': 'NWPL - Mini Dashboard',
    'version': '17.0.0.0.0',
    'category': 'Prescriptions/Sales',
    'summary': 'Mini dashboard for Prescriptions and Sales, Displays the total amount and count of Quotations and Sale Orders',
    'description': """This module is developed for displaying the count of prescriptions and sale orders, total amount for sale orders and total amount for quotations.""",
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'base',
        'pod_prescription_management',
        'sale_management',
    ],
    'data': [
        'views/prescription_order_views.xml',
        'views/sale_order_views.xml',
        ],
    'assets': {
        'web.assets_backend': [
            'pod_mini_dashboard/static/src/xml/*.xml',
            'pod_mini_dashboard/static/src/js/*.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
