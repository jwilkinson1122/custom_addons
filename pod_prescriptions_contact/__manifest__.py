# -*- coding: utf-8 -*-

{
    'name': 'NWPL Contacts',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Contacts',
    'sequence': 0,
    'summary': 'Centralize contacts',
    'description': """Manage contacts directory""",
    'depends': [
        # 'pod_qrcode',
        # 'pod_barcodes_abstract',
        # 'pod_barcodes_partner',
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
            'pod_prescriptions_contact/static/src/css/custom.css',
            'pod_prescriptions_contact/static/scss/custom_form.scss',
            # 'pod_prescriptions_contact/static/src/css/custom.css',
            # 'pod_prescriptions_contact/static/src/js/partner_hierarchy.js',
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
            'pod_prescriptions_contact/static/tests/tours/**/*',
        ],
    }
}
