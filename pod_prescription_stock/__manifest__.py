# -*- coding: utf-8 -*-


{
    'name': 'NWPL - Prescription and Warehouse Management',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'website': 'https://www.nwpodiatric.com',
    'category': 'Hidden',
    'summary': 'Link prescription and warehouses management applications',
    'description': """Link prescription and warehouses management applications.""",
    'depends': [
        'pod_prescription', 
        'stock_account'
        ],
    'data': [
        'security/prescription_stock_security.xml',
        'security/ir.model.access.csv',

        'views/prescription_order_views.xml',
        'views/stock_route_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_stock_portal_template.xml',
        'views/stock_lot_views.xml',
        'views/res_users_views.xml',

        'report/prescription_order_report_templates.xml',
        'report/stock_report_deliveryslip.xml',

        'data/mail_templates.xml',
        'data/prescription_stock_data.xml',

        'wizard/stock_rules_report_views.xml',
        'wizard/prescription_order_cancel_views.xml',
    ],
    'demo': ['data/prescription_order_demo.xml'],
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_backend': [
            'pod_prescription_stock/static/src/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
