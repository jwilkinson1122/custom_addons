# -*- coding: utf-8 -*-
{
    'name': 'NWPL - Create MRP Order From POS',
    'version': '17.0.0.0.0',
    'category': 'MRP/Point of Sale',
    'summary': 'Create Manufacturing order from pos screen and view the manufacturng order created fom pos',
    'description': '''
        Create Manufacturing order from pos screen and view the manufacturng order created fom pos
    ''',
    'author': 'NWPL',
    'website': 'http://www.nwpodiatric.com',
    'depends': [
        'pod_point_of_sale',
        'mrp'
        ],
    'data': ['views/pos_config_view.xml'],

    "assets": {
        "point_of_sale.assets": [
            # "pod_mrp_order_from_pos/static/src/js/**/*.js",
            # "pod_mrp_order_from_pos/static/src/xml/**/*.xml",
        ],
    },
    "images": ['description/icon.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
    },
}