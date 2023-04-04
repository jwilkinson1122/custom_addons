# -*- coding: utf-8 -*-
{
    'name': 'Prescriptions Organization',
    'version': '1.6',
    'website': 'https://erp.nwpodiatric.com/',
    'category': 'Medical/Prescriptions',
    'summary': 'Prescriptions, Contacts, Registrations',
    'description': """
Organization and management of Prescriptions.
======================================

The prescription module allows you to efficiently organize prescriptions and all related tasks: planning, tracking, etc.

Key Features
------------
* Manage Clinic Prescriptions
* Use emails to automatically confirm and send acknowledgments for any prescription registration
""",
    'depends': ['base_setup', 'mail', 'portal', 'utm'],
    'data': [
        'security/prescription_security.xml',
        'security/ir.model.access.csv',
        'views/prescription_menu_views.xml',
        'views/prescription_ticket_views.xml',
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
        'views/prescription_tag_views.xml'
    ],
    'demo': [
        'data/res_users_demo.xml',
        'data/res_partner_demo.xml',
        'data/prescription_demo_misc.xml',
        'data/prescription_demo.xml',
        'data/prescription_registration_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
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
            '/prescription/static/src/scss/prescription_full_page_ticket_report.scss',
        ],
        'web.report_assets_pdf': [
            '/prescription/static/src/scss/prescription_full_page_ticket_report_pdf.scss',
        ],
    },
    'license': 'LGPL-3',
}
