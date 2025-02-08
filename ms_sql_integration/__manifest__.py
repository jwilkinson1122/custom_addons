# -*- coding: utf-8 -*-
#############################################################################
# Author: Fasil
# Email: fasilwdr@hotmail.com
# WhatsApp: https://wa.me/966538952934
# Facebook: https://www.facebook.com/fasilwdr
# Instagram: https://www.instagram.com/fasilwdr
#############################################################################

{
    'name': 'Integration - MS SQL to Odoo',
    'version': '17.0.1.0.3',
    'sequence': 1,
    'summary': """Integrate MS SQL data to Odoo""",
    'description': """"This module help to integrate data from MS SQL to odoo""",
    'category': 'Extra Tools',
    'author': 'Fasil',
    'company': 'Fasil',
    'website': "http://www.facebook.com/fasilwdr",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/sql_integration.xml',
    ],
        'assets': {
           'web.assets_backend': [
               'ms_sql_integration/static/src/scss/scss_by_fas.scss',
           ],
        },
    'qweb': [],
    'images': [
        'static/description/banner.png'
    ],
    'license': 'OPL-1',
    'currency': 'USD',
    'price': '59',
    'installable': True,
    'auto_install': False,
    'application': False,
    'external_dependencies': {
        'python': ['pyodbc'],
    },
}

#############################################################################