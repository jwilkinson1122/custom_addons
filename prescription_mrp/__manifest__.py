# -*- coding: utf-8 -*-



{
    'name': 'Prescription and MRP Management',
    'version': '17.0.0.0.0',
    'category': 'Inventory/Prescription',
    'description': """
This module provides facility to the user to install mrp and prescription modules at a time.
========================================================================================

It is basically used when we want to keep track of production orders generated
from prescription order.
    """,
    'data': [
        'views/mrp_bom_views.xml',
        'views/prescription_order_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_orderpoint_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/prescription_mrp_demo.xml',
    ],
    'depends': ['mrp', 'prescription_stock'],
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_backend': [
            'mrp/static/src/**/*.js',
        ],
    },
    'license': 'LGPL-3',
}
