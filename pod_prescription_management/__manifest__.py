# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescription Management',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescription',
    'sequence': 5,
    'summary': 'From quotations to invoices',
    'description': """Manage prescription orders.""",
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'pod_prescription', 
        'digest'
        ],
    'data': [
        # 'data/digest_data.xml',

        'security/ir.model.access.csv',
        'security/prescription_management_security.xml',

        'report/prescription_report_templates.xml',

        # Define SO template views & actions before their place of use
        'views/prescription_order_template_views.xml',

        # 'views/digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_order_views.xml',
        'views/prescription_portal_templates.xml',

        'views/prescription_management_menus.xml',
    ],
    'demo': [
        'data/prescription_order_template_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pod_prescription_management/static/src/js/**/*',
        ],
    },
    'application': True,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
