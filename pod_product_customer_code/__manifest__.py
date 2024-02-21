# -*- coding: utf-8 -*-
{
    "name": "NWPL - Product Customer Code",
    "author": "NWPL",
    "license": "LGPL-3",
    "website": "https://www.nwpodiatric.com",
    "category": "Sales",
    "summary": "Manage Partner Product Code",
    "description": """Manage specific product codes for customers.""",
    "version": "17.0.0.0.0",
    'depends': [
        'prescription_management',
        'sale_management',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/product_customer_info_groups.xml',

        'views/res_config_settings_views.xml',
        'views/product_template_views.xml',
        'views/product_customer_info_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',

        'report/sale_order_report_views.xml',
        'report/account_move_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_product_customer_code/static/src/scss/custom.scss',
        ],
    },

    'images': ['static/description/icon.png', ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
