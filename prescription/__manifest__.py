# -*- coding: utf-8 -*-

{
    'name' : 'NWPL - Prescription Base',
    'version': '17.0.0.0.0',
    'author': 'NWPL',
    'sequence': 185,
    'category': 'Prescription Base',
    'website' : 'https://www.nwpodiatric.com',
    'summary' : 'Manage your prescription and track prescription costs',
    'description' : """Add options to your prescription. Show all costs associated to a prescription.""",
    'depends': [
        'base',
        'mail',
        'currency_rate_live',
    ],
    'data': [
        'security/prescription_security.xml',
        'security/ir.model.access.csv',
        'views/prescription_type_model_views.xml',
        'views/prescription_type_views.xml',
        'views/prescription_type_cost_views.xml',
        'views/prescription_board_view.xml',
        'views/mail_activity_views.xml',
        'views/res_config_settings_views.xml',
        'data/prescription_type_data.xml',
        'data/prescription_data.xml',
        'data/mail_message_subtype_data.xml',
        'data/mail_activity_type_data.xml',
    ],

    'demo': [
        'data/prescription_demo.xml',
        ],

    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'prescription/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
