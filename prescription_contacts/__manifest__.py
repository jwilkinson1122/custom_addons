# -*- coding: utf-8 -*-

{
    'name': 'NWPL Contacts',
    'version': '17.0.0.0.0',
    'sequence': 1,
    "author": "NWPL",
    'category': 'Contacts',
    'summary': 'Centralize medical contacts',
    'website': 'https://www.nwpodiatric.com',
    'description': """Manage contacts directory""",
    'depends': [
        'base',
        "base_setup", 
        'mail',
        'contacts',
        ],
    'data': [
        'security/prescription_security.xml',
        'security/flag_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/prescription_practice_type.xml',
        'data/prescription_role.xml',
        'views/prescription_role.xml',
        'views/prescription_diagnosis.xml',
        # 'views/contact_views.xml',
        'views/res_partner.xml',
        'views/prescription_menu.xml',
        'views/prescription_practice_type.xml',
        'views/prescription_patient.xml',
        'views/prescription_flag_views.xml',
        'views/prescription_flag_category_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'prescription_contacts/static/src/css/custom.css',
            'prescription_contacts/static/scss/custom_form.scss',
            # 'prescription_contacts/static/src/css/custom.css',
            # 'prescription_contacts/static/src/js/partner_hierarchy.js',
        ],
    },
    'demo': [
        'data/mail_demo.xml',
        'data/contacts_demo.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_tests': [
            'prescription_contacts/static/tests/tours/**/*',
        ],
    }
}
