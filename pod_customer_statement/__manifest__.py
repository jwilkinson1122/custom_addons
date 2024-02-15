# -*- coding: utf-8 -*-

{
    "name": "NWPL - Account Statements",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "version": "17.0.0.0.0",
    "category": "Podiatry", 
    "summary": "Customer Statement",
    "depends": ['account'],
    "data": [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/user.xml',
        'wizard/mail_compose_view.xml',
        'wizard/customer_statement_mass_action.xml',
        'wizard/customer_config_update_wizard.xml',
        'views/mail_history.xml',
        'views/res_config_setting.xml',
        'views/res_partner.xml',
        'views/customer_statement_menu.xml',
        'report/customer_statement_report.xml',
        'report/customer_due_statement_report.xml',
        'report/customer_filter_statement_report.xml',
        'data/email_data.xml',
        'data/statement_cron.xml',
        'views/customer_statement_portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': ['pod_customer_statement/static/src/js/portal.js']
    },
    'images': ['static/description/icon.png'],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True,
}
