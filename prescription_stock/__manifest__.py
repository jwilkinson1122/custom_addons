# -*- coding: utf-8 -*-
{
    'name': "NWPL - Prescription - Stock",
    'summary': """Link Stock with Prescription""",
    'description': """Add types and practitioners assignation on Picking Orders and waves. These Statistics can also be accessed directly from the type view.""",
    'author': "NWPL",
    'website': "https://www.nwpodiatric.com",
    'category': 'Inventory',
    'version': '17.0.0.0.0',
    'depends': [
        'stock', 
        'stock_sms',
        'prescription'
        ],
    'images': ['static/src/description/icon.png'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        'views/prescription_view.xml',
    ],
}