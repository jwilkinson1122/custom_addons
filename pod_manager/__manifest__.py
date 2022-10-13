# -*- coding: utf-8 -*-
#############################################################################

{
    'name': 'Podiatry Manager',
    'version': '15.0.1.0.0',
    'summary': """This module will helps you manage patients, practitioners, and prescriptions.""",
    'description': " ",
    'category': "Medical",
    'author': 'NWPL',
    'website': "https://www.nwpodiatric.com",
    'depends': ['base', 'account', 'podiatry', 'mail'],
    'data': [
        'data/podiatry_manager_data.xml',
        'security/manager_security.xml',
        'security/ir.model.access.csv',
        'views/product_manager_view.xml',
        'views/checklist_view.xml',
        'views/product_tools_view.xml',
        'reports/manager_report.xml'
    ],
    'demo': [
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
