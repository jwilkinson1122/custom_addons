# -*- coding: utf-8 -*-
# Copyright 2021 RL Software Development ApS. See LICENSE file for full copyright and licensing details.
{
    'name': "Products - improvements",

    'summary': """
       Extra features for products. Fx. follow products insted of using KIT.""",

    'description': """
        Contact Mads Christensen for more information
    """,

    'author': "RL Software Development ApS",
    'website': "https://www.rlsd.dk/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '17.0.1.0.3',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'sale',
        'base'
    ],

    # always loaded
    'data': [      
        'views/view_product_template.xml',
        'views/view_sale.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}