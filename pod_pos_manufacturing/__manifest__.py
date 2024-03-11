# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Manufacturing',
    'version': '17.0.0.0.0',
    'category': 'Sales/Point of Sale',
    'sequence': 6,
    'summary': 'Warehouse extensions for the Point of Sale ',
    'description': """
This module adds several features to the Point of Sale that are specific to warehouse management:
- Invoice Printing: Allows you to print a receipt before the order is paid
- Invoice Splitting: Allows you to split an order into different orders
- Warehouse Order Printing: allows you to print orders updates to warehouse printers
""",
    'depends': ['pod_point_of_sale'],
    'website': 'https://www.nwpodiatric.com',
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order_views.xml',
        'views/pos_manufacturing_views.xml',
        'views/res_config_settings_views.xml',
        'data/pos_manufacturing_data.xml',
    ],
    'demo': [
        'data/pos_manufacturing_demo.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pod_pos_manufacturing/static/src/**/*',
            ('after', 'pod_point_of_sale/static/src/scss/pos.scss', 'pod_pos_manufacturing/static/src/scss/manufacturing.scss'),
        ],
        'web.assets_backend': [
            'pod_point_of_sale/static/src/scss/pos_dashboard.scss',
        ],
        'web.assets_tests': [
            'pod_pos_manufacturing/static/tests/tours/**/*',
        ],
    },
    'license': 'LGPL-3',
}
