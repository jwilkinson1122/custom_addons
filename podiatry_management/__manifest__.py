# -*- coding: utf-8 -*-

{
    'name': 'Podiatry Management',
    'version': '15.0.1.0.1',
    'summary': """Complete Prescription Service Management""",
    'description': 'This module is very useful to manage all process of prescription service',
    "category": "Industries",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'mail', 'sale', 'account', 'uom'],
    'data': [
        'data/data.xml',
        'security/prescription_security.xml',
        'security/ir.model.access.csv',
        'views/prescription_view.xml',
        'views/washing_view.xml',
        'views/config_view.xml',
        'views/prescription_report.xml',
        'views/prescription_label.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
