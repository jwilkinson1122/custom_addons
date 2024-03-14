# -*- coding: utf-8 -*-
{
    'name': "Product Extension Dimensions",
    'sequence': 1,
    'application': True,
    'summary': """
        Product Dimensions on Product Templates
        """,

    'description': """
        Adding Dimensions on Product Template.
    """,
    'images': [],
    'author': "Mohamed Yaseen Dahab",
    'version': '17.0.0.0.0',
    'license': "AGPL-3",
    'category': "Purchase Management",
    'depends': ['base', 'purchase','sale', 'stock','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_line_report.xml',
        'views/inherit_sale_order_view.xml',
        'views/inherit_purchase_order_view.xml',
        'views/inherit_stock_view.xml',
        'wizard/mo_view.xml',
        # 'views/inherit_account_view.xml',

    ]
}
