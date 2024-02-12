# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescription Management',
    "author": "NWPL",
    'version': '17.0.0.0.0',
    'category': 'Podiatry/Prescription',
    'sequence': 5,
    'summary': 'From quotations to invoices',
    'description': """
Manage prescription quotations and orders
==================================

This application allows you to manage your prescription goals in an effective and efficient manner by keeping track of all prescription orders and history.

It handles the full prescription workflow:

* **Draft Rx** -> **Prescription order** -> **Invoice**

Preferences (only with Warehouse Management installed)
------------------------------------------------------

If you also installed the Warehouse Management, you can deal with the following preferences:

* Shipping: Choice of delivery at once or partial delivery
* Invoicing: choose how invoices will be paid
* Incoterms: International Commercial terms


With this module you can personnalize the prescription order and invoice report with
categories, subtotals or page-breaks.

The Dashboard for the Prescription Manager will include
------------------------------------------------
* My Prescription
* Monthly Turnover (Graph)
    """,
    'website': 'https://www.nwpodiatric.com',
    'depends': [
        'prescription', 
        'digest'
        ],
    'data': [
        # 'data/digest_data.xml',

        'security/ir.model.access.csv',
        'security/prescription_management_security.xml',

        'report/prescription_report_templates.xml',

        # Define SO template views & actions before their place of use
        'views/prescription_template_views.xml',

        # 'views/digest_views.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_views.xml',
        'views/prescription_portal_templates.xml',

        'views/prescription_management_menus.xml',
    ],
    'demo': [
        'data/prescription_template_demo.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'prescription_management/static/src/js/**/*',
        ],
    },
    'application': True,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
