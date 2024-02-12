# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt Ltd. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Blanket Sales Order Portal',
    'version' : '17.0.0.0.0',
    'price': 49.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Blanket Sales Order Portal Odoo App',
    'description': """
       Blanket Sales Order Portal for Customer on My Account
    """,
    'author': "Probuse Consulting Service Pvt. Ltd.",
    'website': "http://www.probuse.com",
    'support': 'contact@probuse.com',
    'category': 'Sales/Sales',
    'images': ['static/description/bso_image.jpg'],
    'live_test_url': 'https://probuseappdemo.com/probuse_apps/prescription_portal/1299',
    'depends' : [
        'portal', 
        'prescription' 
    ],
    'data': [
        # 'security/security.xml',
        'security/ir.model.access.csv',
        'views/portal_view.xml',
    ],
   
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
