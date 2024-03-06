# -*- coding: utf-8 -*-
{
    'name': 'NWPL - MRP Orders from POS',
    'version': '17.0.0.0.0',
    'category': 'Point of Sale',
    'summary': """Generate Automatic MRP orders from POS.""",
    'description': """This module enables to create automatic MRP orders after 
    selling through POS.""",
    'author': 'NWPL',
    'website': "https://www.nwpodiatric.com",
    'depends': [
        'pod_point_of_sale', 
        'mrp', 
        'stock'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pod_pos_mrp_order/static/src/js/payment_screen.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False
}
