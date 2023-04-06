# -*- coding: utf-8 -*-
{
    'name': 'Prescription Management',
    'version': '1.0',
    'website': 'https://erp.nwpodiatric.com/',
    'category': 'Medical/Prescriptions',
    'summary': 'Prescriptions, Contacts, Validations',
    'description': """
Organization and management of Prescriptions.
======================================

The prescription module allows you to efficiently organize prescriptions and all related tasks: planning, tracking, etc.

Key Features
------------
* Manage Clinic Prescriptions
* Use emails to automatically confirm and send acknowledgments for any prescription validation
""",
    'depends': ['base_setup', 'mail', 'portal', 'utm','sale',
        'sale_management',],
    'data': [
        'security/prescription_security.xml',
        'security/ir.model.access.csv',
        'views/prescription_menu_views.xml',
        'views/prescription_device_views.xml',
        'views/prescription_views.xml',
        'views/prescription_stage_views.xml',
        'report/prescription_prescription_templates.xml',
        'report/prescription_prescription_reports.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/prescription_data.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_templates.xml',
        'views/res_partner_views.xml',
        "views/podiatry_patient.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_practitioner.xml",
        'views/prescription_tag_views.xml'
    ],
    'demo': [
        'data/res_users_demo.xml',
        'data/res_partner_demo.xml',
        'data/prescription_demo_misc.xml',
        'data/prescription_demo.xml',
        'data/prescription_confirmation_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    "application": True,
    'assets': {
        'web.assets_backend': [
            'prescription/static/src/scss/prescription.scss',
            'prescription/static/src/js/field_icon_selection.js',
        ],
        'web.assets_common': [
            'prescription/static/src/js/tours/**/*',
        ],
        'web.assets_qweb': [
            'prescription/static/src/xml/**/*',
        ],
        'web.report_assets_common': [
            '/prescription/static/src/scss/prescription_foldable_badge_report.scss',
            '/prescription/static/src/scss/prescription_full_page_device_report.scss',
        ],
        'web.report_assets_pdf': [
            '/prescription/static/src/scss/prescription_full_page_device_report_pdf.scss',
        ],
    },
    "author": "NWPL",
    # "license":'OPL-1',
    "development_status": "Beta",
}
