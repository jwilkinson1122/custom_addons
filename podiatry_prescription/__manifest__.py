# -*- coding: utf-8 -*-
{
    'name': "Prescription Order",

    'summary': """
        Prescription Order NWPL""",

    'description': """
        Prescription Order NWPL
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
        "resource",
        'sale', 
        'sale_management', 
        'sale_stock',
        'sale_product_configurator',
        'stock',
        'product', 
        'uom',
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
        "data/ir_sequence_data.xml",
        'wizard/wizard_cancelled.xml',
        'views/work_order_views.xml',
        'views/podiatry_prescription_views.xml',
        "views/actions.xml",
        'views/menu.xml',
        'report/report_work_order.xml',
        'report/report.xml',
        # 'wizard/wizard_cancelled.xml',
    ],
    "assets": {
        "web.assets_backend": [

        ],
    },
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    "images": ["static/description/icon.png"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
