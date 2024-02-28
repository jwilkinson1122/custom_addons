# -*- coding: utf-8 -*-

{
    'name': "NWPL - Spreadsheet CRM Templates",
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Spreadsheet CRM templates',
    'description': 'Spreadsheet CRM templates',
    'depends': ['prescriptions_spreadsheet', 'crm'],
    'data': [
        'data/spreadsheet_template_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_tests': [
            'prescriptions_spreadsheet_crm/static/**/*',
        ],
    }
}
