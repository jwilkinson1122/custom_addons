# -*- coding: utf-8 -*-

{
    'name': 'Product Matrix',
    'version': '16.0.0.0',
    'category': 'Sales',
    'summary': 'Sales Order Product Matrix',
    'description': """Add Custom Product Matrix""",
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com.com',
    'depends': [
        'sale',
        'sale_management', 
        'stock', 
        'account'
        ],
    'data': [
        'security/product_sm_group.xml',
        'security/ir.model.access.csv',
        'data/product_sm_demo.xml',
        'wizard/matrix_wizard.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    # "images":['static/description/'],
}
