# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Blanket Sales Order',
    'version': '17.0.0.0.0',
    'price': 49.0,
    'category' : 'Sales',
    'license': 'Other proprietary',
    'currency': 'EUR',
    'summary': """Blanket Sales Order Management""",
    'description': """
This module allows you to manage your prescription order.
Manage prescriptions. Blanket orders
are agreements you have with customers to benefit from a predetermined pricing.   
Blanket Sales Order
prescription
prescription order
prescriptions

    """,
    'author': 'Probuse Consulting Service Pvt. Ltd.',
    'website': 'http://www.probuse.com',
    'support': 'contact@probuse.com',
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/prescription/801',#'https://youtu.be/pGeHRkyetiI',
    'images': [
               'static/description/image.png'
    ],
    'depends': [
        'sale',
        'sale_management',
        'account'
    ],
    'data':[
        'security/ir.model.access.csv',
        'security/prescription_security.xml',
        'data/prescription_sequence.xml',
        'views/prescription_view.xml',
        'views/sale_order_view.xml',
        'report/prescription_report.xml',
        'views/menu.xml'
    ],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
