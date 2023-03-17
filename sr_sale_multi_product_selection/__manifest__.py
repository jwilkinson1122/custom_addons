# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': "Sale Order Multi Product Selection",
    'version': "13.0.0.1",
    'summary': "This module allows you to select Multiple product in sale order at a time on single click.",
    'category': 'Sale Management',
    'description': """
        This module allows you to select Multiple product in sale order on single click.
         sale order add multi product
         product add
         multiple product add in sale order quickly
         easy add product in sale order on single click
         create sale order from product
    """,
    'author': "Sitaram",
    'website': "sitaramsolutions.in",
    'depends': ['base', 'sale_management', 'product'],
    'data': [
            'security/ir.model.access.csv',
        'views/sale.xml',
        'views/product.xml'
    ],
    'demo': [],
    "license": "OPL-1",
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://youtu.be/0KFUawEdMpk',
    'installable': True,
    'application': True,
    'auto_install': False,
}
