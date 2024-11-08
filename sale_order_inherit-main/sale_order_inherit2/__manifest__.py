{
    'name': "Sale Order Inherit",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'stock', 'purchase','sale_management'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "views/sale_order_views.xml",
        "views/product_template_views.xml",
        "views/purchase_order_views.xml",
        "views/configuration_booking_order_views.xml",
        "views/menus.xml",
    ],
    'installable': True,
    'application': True,
}
# -*- coding: utf-8 -*-
