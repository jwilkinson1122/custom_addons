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
    'category': 'Sales',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'product_configurator', 'product_configurator_sale', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_cancelled.xml',
        'views/service_team_views.xml',
        'views/work_order_views.xml',
        'views/booking_order_views.xml',
        'views/menu.xml',
        'report/report_work_order.xml',
        'report/report.xml',
        'data/data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
