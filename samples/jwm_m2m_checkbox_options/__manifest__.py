# -*- coding: utf-8 -*-
{
    'name': "many2many fields checkbox customizes",

    'description': """
        many2many fields checkbox customizes how many columns to display
    """,

    'author': "jj190214@163.com",

    'category': 'Tools',
    'version': '16.0',
    'license': 'OPL-1',
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/m2m_checkbox_options.xml',
        'views/menuitem.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'jwm_m2m_checkbox_options/static/src/js/*.js',
            'jwm_m2m_checkbox_options/static/src/xml/*.xml',
        ],
    },
    'images': [
        'static/description/multi_selection.png',
    ],
    'installable': True,
    'active': True,
    'auto_install': False,
}
