# -*- coding: utf-8 -*-
{
    'name': "NWPL - Prescription - Sale",
    'summary': """Link Sales with Prescription""",
    'description': """Add types and practitioners assignation on Quotes and Sale Orders. These Statistics can also be accessed directly from the type view.""",
    'author': "NWPL",
    'website': "https://www.nwpodiatric.com",
    'category': 'Sales',
    'version': '17.0.0.0.0',
    'depends': [
        'sale', 
        'sale_management',
        'prescription_stock', 
        'sale_stock'
        ],
    'images': ['static/src/description/icon.png'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
        'views/prescription_view.xml',
    ],
}