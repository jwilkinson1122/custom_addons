# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Contact Management',
    'version': '17.0.0.0.0',
    'license': 'LGPL-3',
    'sequence': 1,
    'author': 'NWPL',
    'category': 'Contacts',
    'summary': 'Centralize Podiatry Contacts',
    'website': 'https://www.nwpodiatric.com',
    'description': """Manage contacts directory""",
    'depends': [
        'base',
        'base_setup', 
        'mail',
        'contacts',
        'pod_custom_theme',
        # 'pod_prescription',
        ],
    'data': [
        'security/contacts_security.xml',
        'security/flag_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/prescription_practice_type.xml',
        'data/prescription_role.xml',
        'views/prescription_role.xml',
        'views/prescription_diagnosis.xml',
        'views/res_partner.xml',
        # 'views/prescription_menu.xml',
        'views/prescription_practice_type.xml',
        'views/prescription_patient.xml',
        'views/prescription_flag_views.xml',
        'views/prescription_flag_category_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_prescription_contacts/static/src/css/custom.css',
            'pod_prescription_contacts/static/scss/custom_form.scss',
            # 'pod_prescription_contacts/static/src/css/custom.css',
            # 'pod_prescription_contacts/static/src/js/partner_hierarchy.js',
        ],
    },
    'demo': [
        'data/mail_demo.xml',
        'data/contacts_demo.xml',
    ],
    'assets': {
        'web.assets_tests': [
            'pod_prescription_contacts/static/tests/tours/**/*',
        ],
    },

    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
}
