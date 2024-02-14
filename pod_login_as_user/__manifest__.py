# -*- coding: utf-8 -*-
{
    'name': 'NWPL - Login as another user',
    'summary': 'Authenticate/Impersonate another user',
    'version': '17.0.0.0.0',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'license': 'LGPL-3',
    'depends': [
        'web',
        'portal',
    ],
    'data': [
        'views/login_as.xml',
        'views/templates.xml',
        'security/ir.model.access.csv',
        'views/action.xml'
    ],
    'assets': {
        'web.assets_backend': [
            '/pod_custom_theme/static/src/scss/pod_theme.scss',
        ],
    },
    'assets': {
        'web.assets_backend': [
            'pod_login_as_user/static/src/login_as/*.js',
            'pod_login_as_user/static/src/login_as/*.xml',
        ],
    },
    'images': ['static/description/icon.png'],
    'auto_install': True,
    'installable': True,
    'application': False,
}
