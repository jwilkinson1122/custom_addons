# -*- coding: utf-8 -*-

{
    "name": "Product Fields",
    'version': '17.0.0.0.0',
    "author": "Bytelegion",
    "website": "http://www.bytelegions.com",
    'company': 'Bytelegion',
    'depends': ['base', 'sale'],
    'license': 'LGPL-3',
    "category": 'Customizations for Products',

    "summary": ' Product Customization',
    "description": """This Module is used to add more product details. 
    Also used for ad customer licence number""",

    'data': [
        'views/inherit_product_fields_view.xml',
        'views/sale_orderline_fields_view.xml',
        'views/invoice_orderline_fields_view.xml',
        'views/customer_view.xml',
        # 'views/inventory_view.xml',
        'report/new_try.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.gif'], 
    
}
