# -*- coding: utf-8 -*-
{
    'name': 'NWPL - Python Version Display',
    'version': '17.0.0.0.0',
    'summary': """Display Python Version and List Of Packages Installed.""",
    'description': """Display Python Version and List Of Packages Installed.""",
    'category': 'Base',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'license': "LGPL-3",
    'depends': ['base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/config_view.xml',
    ],
    'demo': [

    ],
    'qweb': [],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
