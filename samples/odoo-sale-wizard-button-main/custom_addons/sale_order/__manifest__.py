# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{

    'name': 'New Product',
    'version': '1.2',
    'author': 'Sasank',
    'summary': 'Adding new product and adding some kind of variants in that product',
    'sequence': -1,
    'description': """
    Adding new product and adding some kind of variants in that product
     """,
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/report_temp.xml',
        'views/sale_order.xml',

    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
