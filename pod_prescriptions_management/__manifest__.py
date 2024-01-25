# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescriptions Management',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescriptions',
    'summary': 'From quotations to invoices',
    'description': """ """,
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'pod_prescriptions', 
        'digest'
        ],
    'data': [
        # 'data/digest_data.xml',

        'security/ir.model.access.csv',
        'security/prescriptions_management_security.xml',

        'report/prescriptions_report_templates.xml',

        # Define RX template views & actions before their place of use
        'views/prescriptions_order_template_views.xml',

        # 'views/digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescriptions_order_views.xml',
        'views/prescriptions_portal_templates.xml',

        'views/prescriptions_management_menus.xml',
    ],
    'demo': [
        'data/prescriptions_order_template_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pod_prescriptions_management/static/src/js/**/*',
        ],
    },
    'application': True,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
