# -*- coding: utf-8 -*-
{
    "name": "NWPL - Website Product Customer Code",
    "author": "NWPL",
    "license": "LGPL-3",
    "website": "https://www.nwpodiatric.com",
    "category": "Website",
    "summary": "Manage Website Partner Product Code",
    "description": """Manage specific product codes for customers at the website.""",
    "version": "17.0.0.0.0",
    'depends': [
        'website_sale',
        'pod_product_customer_code'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/website_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'pod_product_customer_code_website/static/src/js/product_customer_code_website.js'
        ],
    },

    'images': ['static/description/icon.png', ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
