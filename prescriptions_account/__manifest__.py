# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescriptions - Accounting',
    'version': '17.0.0.0.0',
    'category': 'Medical/Prescriptions',
    'summary': 'Invoices from Prescriptions',
    'description': """
Bridge module between the accounting and prescriptions apps. It enables
the creation invoices from the Prescriptions module, and adds a
button on Accounting's reports allowing to save the report into the
Prescriptions app in the desired format(s).
""",
    'website': ' ',
    'depends': ['prescriptions', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/prescriptions_workflow_data.xml',
        'data/mail_activity_type_data.xml',
        'views/account_move_views.xml',
        'views/prescriptions_account_folder_setting_views.xml',
        'views/prescriptions_workflow_rule_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/account_reports_export_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'prescriptions_account/static/**/*',
        ],
    }
}
