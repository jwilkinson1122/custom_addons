# -*- coding: utf-8 -*-

{
    'name': "NWPL - Spreadsheet Accounting Templates",
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Spreadsheet Accounting templates',
    'description': 'Spreadsheet Accounting templates',
    'depends': ['prescriptions_spreadsheet', 'account'],
    'data': [
        'data/spreadsheet_template_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_tests': [
            'prescriptions_spreadsheet_account/static/**/*',
        ],
    }
}
