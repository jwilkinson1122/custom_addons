# -*- coding: utf-8 -*-
{
    'name': 'Many2one Wizard Widget',
    'version': '17.0.1.0',
    'category': 'Extra Tools',
    'summary': """Opens many2one field as a wizard""",
    'description': """ Updates Below
    - Create a widget named wizard_mto.
    - Many2one fields can be opened as a wizard.
    """,
    'author': 'Mohammed Amal',
    'maintainer': 'Mohammed Amal',
    'depends': [
        'base',
    ],
    'assets': {
        'web.assets_backend': [
            'wizard_mto_ma/static/src/**/*',
        ],

    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
