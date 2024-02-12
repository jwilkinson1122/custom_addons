# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescription and Warehouse Management',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Hidden',
    'summary': 'Draft Rx, Prescription Orders, Delivery & Invoicing Control',
    'description': """
Manage prescription quotations and orders
==================================

This module makes the link between the prescription and warehouses management applications.

Preferences
-----------
* Shipping: Choice of delivery at once or partial delivery
* Invoicing: choose how invoices will be paid
* Incoterms: International Commercial terms

""",
    'depends': [
        'prescription', 
        'stock_account'
        ],
    'data': [
        'security/prescription_stock_security.xml',
        'security/ir.model.access.csv',

        'views/prescription_views.xml',
        'views/stock_route_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_stock_portal_template.xml',
        'views/stock_lot_views.xml',
        'views/res_users_views.xml',

        'report/prescription_report_templates.xml',
        'report/stock_report_deliveryslip.xml',

        'data/mail_templates.xml',
        'data/prescription_stock_data.xml',

        'wizard/stock_rules_report_views.xml',
        'wizard/prescription_cancel_views.xml',
    ],
    'demo': ['data/prescription_demo.xml'],
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_backend': [
            'prescription_stock/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
