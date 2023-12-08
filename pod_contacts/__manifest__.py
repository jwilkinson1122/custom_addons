# -*- coding: utf-8 -*-

{
    'name': 'NWPL Contacts',
    "author": "NWPL",
    'category': 'Podiatry/Contacts',
    'sequence': 150,
    'summary': 'Centralize contacts',
    'description': """Manage contacts directory""",
    'depends': [
        'base',
        "base_setup", 
        'mail',
        'contacts',
        ],
    'data': [
        'security/pod_security.xml',
        'security/flag_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/pod_practice_type.xml',
        'data/pod_role.xml',
        'views/pod_role.xml',
        'views/pod_diagnosis.xml',
        # 'views/contact_views.xml',
        'views/res_partner.xml',
        'views/pod_menu.xml',
        'views/pod_practice_type.xml',
        'views/pod_patient.xml',
        'views/pod_flag_views.xml',
        'views/pod_flag_category_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_contacts/static/src/css/custom.css',
            'pod_contacts/static/scss/custom_form.scss',
            # 'pod_contacts/static/src/css/custom.css',
            # 'pod_contacts/static/src/js/partner_hierarchy.js',
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
            'pod_contacts/static/tests/tours/**/*',
        ],
    }
}
