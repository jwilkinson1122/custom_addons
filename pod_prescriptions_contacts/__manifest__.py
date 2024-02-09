# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Contact Management',
    'version': '17.0.0.0.0',
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
        ],
    'data': [
        'security/contacts_security.xml',
        'security/flag_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/prescriptions_practice_type.xml',
        'data/prescriptions_role.xml',
        'views/prescriptions_role.xml',
        'views/prescriptions_diagnosis.xml',
        'views/res_partner.xml',
        # 'views/prescriptions_menu.xml',
        'views/prescriptions_practice_type.xml',
        'views/prescriptions_patient.xml',
        'views/prescriptions_flag_views.xml',
        'views/prescriptions_flag_category_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescriptions_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_prescriptions_contacts/static/css/custom.css',
            'pod_prescriptions_contacts/static/scss/custom_form.scss',
            # 'pod_prescriptions_contacts/static/src/js/partner_hierarchy.js',
            # 'pod_prescriptions_contacts/static/js/org_chart.js',
            # 'pod_prescriptions_contacts/static/xml/org_chart.xml',
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
            'pod_prescriptions_contacts/static/tests/tours/**/*',
        ],
    }
}
