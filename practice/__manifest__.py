# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pod ERP',
    'version': '1.1',
    'category': 'Medical',
    'sequence': 95,
    'summary': 'Centralize podiatry partner information',
    'description': "",
    'website': 'https://www.nwpodiatric.com',
    'images': [
        'images/podiatry_practice.jpeg',
        'images/podiatry_employee.jpeg',
        'images/podiatry_job_position.jpeg',
        'static/src/img/default_image.png',
    ],
    'depends': [
        'base_setup',
        'mail',
        'resource',
        'web',
    ],
    'data': [
        'security/podiatry_security.xml',
        'security/ir.model.access.csv',
        'wizard/podiatry_plan_wizard_views.xml',
        'wizard/podiatry_inactive_wizard_views.xml',
        'views/podiatry_inactive_reason_views.xml',
        'views/podiatry_job_views.xml',
        'views/podiatry_plan_views.xml',
        'views/podiatry_employee_category_views.xml',
        'views/podiatry_employee_public_views.xml',
        'report/podiatry_employee_badge.xml',
        'views/podiatry_employee_views.xml',
        'views/podiatry_practice_views.xml',
        'views/podiatry_practice_location_views.xml',
        'views/podiatry_views.xml',
        'views/res_config_settings_views.xml',
        'views/mail_channel_views.xml',
        'views/res_users.xml',
        'views/res_partner_views.xml',
        'data/podiatry_data.xml',
    ],
    'demo': [
        'data/podiatry_demo.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'mail.assets_discuss_public': [
            'podiatry/static/src/models/*/*.js',
        ],
        'web.assets_backend': [
            'podiatry/static/src/scss/podiatry.scss',
            'podiatry/static/src/js/chat_mixin.js',
            'podiatry/static/src/js/podiatry_employee.js',
            'podiatry/static/src/js/language.js',
            'podiatry/static/src/js/m2x_avatar_employee.js',
            'podiatry/static/src/js/standalone_m2o_avatar_employee.js',
            'podiatry/static/src/js/user_menu.js',
            'podiatry/static/src/models/*/*.js',
        ],
        'web.qunit_suite_tests': [
            'podiatry/static/tests/helpers/mock_models.js',
            'podiatry/static/tests/m2x_avatar_employee_tests.js',
            'podiatry/static/tests/standalone_m2o_avatar_employee_tests.js',
        ],
        'web.assets_qweb': [
            'podiatry/static/src/xml/podiatry_templates.xml',
        ],
    },
    'license': 'LGPL-3',
}
