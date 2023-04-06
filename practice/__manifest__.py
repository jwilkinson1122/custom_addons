# -*- coding: utf-8 -*-
{
    'name': 'Practice Management',
    'version': '1.0',
    'website': 'https://erp.nwpodiatric.com/',
    'category': 'Medical/Practices',
    'summary': 'Practices, Contacts, Validations',
    'description': """
Organization and management of Practices.
======================================

The practice module allows you to efficiently organize practices and all related tasks: planning, tracking, etc.

Key Features
------------
* Manage Clinic Practices
* Use emails to automatically confirm and send acknowledgments for any practice validation
""",
    'depends': ['base_setup', 'mail', 'portal', 'utm','sale',
        'sale_management',],
    'data': [
        'security/practice_security.xml',
        'security/ir.model.access.csv',
        'views/practice_menu_views.xml',
        'views/practice_device_views.xml',
        'views/practice_views.xml',
        'views/practice_stage_views.xml',
        'report/practice_practice_templates.xml',
        'report/practice_practice_reports.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/practice_data.xml',
        'views/res_config_settings_views.xml',
        'views/practice_templates.xml',
        'views/res_partner_views.xml',
        "views/podiatry_patient.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_practitioner.xml",
        'views/practice_tag_views.xml'
    ],
    'demo': [
        'data/res_users_demo.xml',
        'data/res_partner_demo.xml',
        'data/practice_demo_misc.xml',
        'data/practice_demo.xml',
        'data/practice_confirmation_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    "application": True,
    'assets': {
        'web.assets_backend': [
            'practice/static/src/scss/practice.scss',
            'practice/static/src/js/field_icon_selection.js',
        ],
        'web.assets_common': [
            'practice/static/src/js/tours/**/*',
        ],
        'web.assets_qweb': [
            'practice/static/src/xml/**/*',
        ],
        'web.report_assets_common': [
            '/practice/static/src/scss/practice_foldable_badge_report.scss',
            '/practice/static/src/scss/practice_full_page_device_report.scss',
        ],
        'web.report_assets_pdf': [
            '/practice/static/src/scss/practice_full_page_device_report_pdf.scss',
        ],
    },
    "author": "NWPL",
    # "license":'OPL-1',
    "development_status": "Beta",
}
