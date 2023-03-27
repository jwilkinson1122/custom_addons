# -*- coding: utf-8 -*-
{
    'name': "Booking Order",

    'summary': """
        Booking Order NWPL""",

    'description': """
        Booking Order NWPL
    """,

    'author': "NWPL",
    'website': "http://www.nwpodiatric.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': [
        'base', 
        "base_setup",
        "resource",
        'sale', 
        'sale_management', 
        'sale_stock',
        'stock',
        'product', 
        'contacts', 
        'mail',
        "account",
        "account_accountant",
        "mail",
        'purchase',
        ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/cancel_order_view.xml',
        # 'wizard/wizard_cancelled.xml',
        'views/work_order_views.xml',
        'views/booking_order_views.xml',
        "views/patient.xml",
        "views/practice.xml",
        "views/practitioner.xml",
        "views/actions.xml",
        'views/menu.xml',
        # "views/partner.xml",
        'report/report_work_order.xml',
        'report/report.xml',
        'data/data.xml',

    ],
    "assets": {
        "web.assets_backend": [
 
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "images": ["static/description/icon.png"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
