# -*- coding: utf-8 -*-

{
    'name': "NWPL - Spreadsheet CRM Templates",
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Spreadsheet CRM templates',
    'description': 'Spreadsheet CRM templates',
    'author': "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'depends': ['prescriptions_spreadsheet', 'crm'],
    'data': [
        'data/spreadsheet_template_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    # 'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_tests': [
            'prescriptions_spreadsheet_crm/static/**/*',
        ],
    }
}
