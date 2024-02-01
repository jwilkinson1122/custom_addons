# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Customer Account Statement",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "17.0.0.0.0",
    "category": "Accounting",  
    "summary": "Customer Payment Followup Print Customer Statement Report Customer Bank Statement Client Statement Contact Statement Overdue Statement Partner Statement of Account Print Overdue Statement send customer statement Account Statement Report Odoo",
    
    "description": """This module allows customers to see statements as well as overdue statement details. You can send statements by email to the customers. You can also see customers mail log history with statements and overdue statements. You can also send statements automatically weekly, monthly & daily using cron job. You can filter statements by dates, statements & overdue statements. You can group by statements by the statement type, mail sent status & customers. You can print statements and overdue statements.""",
    "depends": [
        'account'
    ],

    'assets': {

        'web.assets_frontend': [
            'sh_customer_statement/static/src/js/portal.js',
        ]

    },

    "data": [
        'security/security.xml',
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
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "50",
    "currency": "EUR"
}
