# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescriptions and Warehouse Management',
    "author": "NWPL",
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Draft Rx, Prescriptions Orders, Delivery & Invoicing Control',
    'description': """
Manage prescriptions quotations and orders
==================================

This module makes the link between the prescriptions and warehouses management applications.

Preferences
-----------
* Shipping: Choice of delivery at once or partial delivery
* Invoicing: choose how invoices will be paid
* Incoterms: International Commercial terms

""",
    'depends': [
        'pod_prescriptions', 
        'stock_account'
        ],
    'data': [
        'security/prescriptions_stock_security.xml',
        'security/ir.model.access.csv',

        'views/prescriptions_order_views.xml',
        'views/stock_route_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescriptions_stock_portal_template.xml',
        'views/stock_lot_views.xml',
        'views/res_users_views.xml',

        'report/prescriptions_order_report_templates.xml',
        'report/stock_report_deliveryslip.xml',

        'data/mail_templates.xml',
        'data/prescriptions_stock_data.xml',

        'wizard/stock_rules_report_views.xml',
        'wizard/prescriptions_order_cancel_views.xml',
    ],
    'demo': ['data/prescriptions_order_demo.xml'],
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_backend': [
            'pod_prescriptions_stock/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
