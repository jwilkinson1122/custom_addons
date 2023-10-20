# -*- coding: utf-8 -*-

{
    'name': 'NWPL ERP',
    'version': '1.1',
    'category': 'Podiatry/Practitioners',
    'sequence': 95,
    'summary': 'Centralize practitioner information',
    'description': "",
    'website': 'https://www.odoo.com/app/practitioners',
    'images': [
        'images/pod_practice.jpeg',
        'images/pod_practitioner.jpeg',
        'images/pod_role_position.jpeg',
        'static/src/img/default_image.png',
    ],
    'depends': [
        'base_setup',
        'mail',
        'resource',
        'web',
    ],
    'data': [
        'security/pod_security.xml',
        'security/ir.model.access.csv',
        'wizard/pod_plan_wizard_views.xml',
        'wizard/pod_deactivate_wizard_views.xml',
        'views/pod_deactivate_reason_views.xml',
        'views/pod_role_views.xml',
        'views/pod_plan_views.xml',
        'views/pod_practitioner_category_views.xml',
        'views/pod_practitioner_public_views.xml',
        'views/pod_practitioner_views.xml',
        'views/pod_practice_views.xml',
        'views/pod_practice_location_views.xml',
        'views/pod_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_channel_views.xml',
        'views/res_users.xml',
        'views/res_partner_views.xml',
        'data/pod_data.xml',
    ],
    'demo': [
        'data/pod_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'mail.assets_discuss_public': [
            'pod_manager/static/src/models/*/*.js',
        ],
        'web.assets_backend': [
            'pod_manager/static/src/scss/main.scss',
            'pod_manager/static/src/js/chat_mixin.js',
            'pod_manager/static/src/js/pod_practitioner.js',
            'pod_manager/static/src/js/language.js',
            'pod_manager/static/src/js/m2x_avatar_practitioner.js',
            'pod_manager/static/src/js/standalone_m2o_avatar_practitioner.js',
            'pod_manager/static/src/js/user_menu.js',
            'pod_manager/static/src/models/*/*.js',
        ],
        'web.qunit_suite_tests': [
            'pod_manager/static/tests/helpers/mock_models.js',
            'pod_manager/static/tests/m2x_avatar_practitioner_tests.js',
            'pod_manager/static/tests/standalone_m2o_avatar_practitioner_tests.js',
        ],
        'web.assets_qweb': [
            'pod_manager/static/src/xml/pod_templates.xml',
        ],
    },
    'license': 'LGPL-3',
}
