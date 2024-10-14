# -*- coding: utf-8 -*-

{
    'name': 'Product Matrix on Sales Order',
    'version': '18.0.0.0',
    'category': 'Sales',
    'summary': 'Sales Product Matrix',
    'description': """ """,
    'author': 'NWPL',
    'depends': ['sale_management', 'stock', 'account'],
    'data': [
        'security/product_sm_group.xml',
        'security/ir.model.access.csv',
        'data/product_sm_demo.xml',
        'wizard/matrix_wizard.xml',
        'views/product_view.xml',
        'views/sale_view.xml',
    ],
    "license":'OPL-1',
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
