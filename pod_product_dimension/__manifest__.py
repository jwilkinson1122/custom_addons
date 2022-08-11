# -*- coding: utf-8 -*-
{
    'name': 'Podiatry Products Dimension',
    "version": '15.0.1.0.0',
    'license': 'OPL-1',
    'summary': 'Products Catalog',
    'sequence': 1,
    "author": "NWPL",
    'description': """ Manage products and dimension.""",
    'category': 'Sales',
    'website': 'https://nwpodiatric.com',
    'images':  ['images/logo.png'],
    'depends': ['base', 'product'],
    'data': [
        'security/product_security.xml',
        'views/product_template_view.xml',
        # 'views/product_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
