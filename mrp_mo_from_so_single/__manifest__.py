# -*- coding: utf-8 -*-
{
    'name': "mrp_mo_from_so",
    'application': True,
    'summary': """
        Generate Manufacturing Order MO from Sale Order Allow User to Select BoM Bill of Materials on the fly""",
    'description': """
        Generate Manufacturing Order MO from Sale Order Allow User to Select BoM Bill of Materials on the fly    """,
    'author': "Mohamed Yaseen Dahab",
    'category': 'Manufacturing',
    'version': '17.0.0.0.0',
    'depends': ['base','sale_management', 'purchase','account','stock','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'reports/mo_label.xml',
        'reports/sale_order_report_inherit.xml',
        'reports/invoice_report.xml',
        'reports/work_order_report.xml',
        'views/mrp_production_view.xml',
        'views/inherit_account_view.xml',
        'views/inherit_purchase_order_view.xml',
        'views/inherit_stock_picking_view.xml',
        'views/sale_order_line_views.xml',
        'views/desc_views.xml',
    ],
}
