# -*- coding: utf-8 -*-
{
    'name': "Odoo Amazon S3 Integration",
    'summary': """Amazon S3 with ODOO.""",
    'description': """
        Synchronization of ODOO with Amazon S3.
        Once data created in S3 account, will be reflected in ODOO by justone click.
    """,
    'author': "WoadSoft",
    'website': "https://www.woadsoft.com",
    'category': 'Tools',
    'version': '1.0',
    'depends': ['base', 'mail', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'external_dependencies': {
        'python': ['boto3'],
    },
    'price': 25,
    'currency': 'EUR',
    'license': 'OPL-1',
    'images':["images/banner.gif"]
}
