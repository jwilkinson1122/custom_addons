# -*- coding: utf-8 -*-

{
    'name': 'NWPL Display Python Version ',
    'version': '15.0.0.1',
    'summary': """Display Python Version and List Of Packages Installed.""",
    'description': """Display Python Version and List Of Packages Installed.""",
    'category': 'Base',
    'author': 'NWPL',
    'website': "",
    "license": "LGPL-3",
    'depends': ['base_setup'],

    'data': [
        'security/ir.model.access.csv',
        'views/config_view.xml',
    ],
    'demo': [

    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
