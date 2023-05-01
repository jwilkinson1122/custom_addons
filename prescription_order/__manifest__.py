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
    'category': 'Sales',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_cancelled.xml',
        'views/service_team_views.xml',
        'views/work_order_views.xml',
        'views/prescription_order_views.xml',
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
