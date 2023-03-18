# -*- coding: utf-8 -*-
{
    'name': "Fikri Service",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/menu.xml',
        'views/sparepart_views.xml',
        'views/servis_views.xml',
        'views/order_views.xml',
        'views/pelanggan_views.xml',
        'views/mekanik_views.xml',
        'views/supplier_views.xml',
        'views/pembelian_views.xml',
        'report/report.xml',
        'report/orderpdf.xml',
        'report/orderpdf.xml',
        'report/wizard_orderreport_template.xml',
        'wizard/sparepartdatang_wizard_views.xml',
        'wizard/orderreport_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
