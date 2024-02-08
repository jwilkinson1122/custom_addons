# -*- coding: utf-8 -*-


{
    'name': 'NWPL Prescriptions Management',
    "author": "NWPL",
    'version': '1.0',
    'category': 'Podiatry/Prescriptions',
    'sequence': 5,
    'summary': 'From quotations to invoices',
    'description': """
Manage prescriptions quotations and orders
==================================

This application allows you to manage your prescriptions goals in an effective and efficient manner by keeping track of all prescriptions orders and history.

It handles the full prescriptions workflow:

* **Draft Rx** -> **Prescriptions order** -> **Invoice**

Preferences (only with Warehouse Management installed)
------------------------------------------------------

If you also installed the Warehouse Management, you can deal with the following preferences:

* Shipping: Choice of delivery at once or partial delivery
* Invoicing: choose how invoices will be paid
* Incoterms: International Commercial terms


With this module you can personnalize the prescriptions order and invoice report with
categories, subtotals or page-breaks.

The Dashboard for the Prescriptions Manager will include
------------------------------------------------
* My Prescriptions
* Monthly Turnover (Graph)
    """,
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

        # Define SO template views & actions before their place of use
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
