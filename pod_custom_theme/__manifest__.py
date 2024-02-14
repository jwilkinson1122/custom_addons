{
    'name': 'NWPL - Custom Theme',
    'summary': 'Contrasted style on fields to improve the UI.',
    'version': '17.0.0.0.0',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            '/pod_custom_theme/static/src/scss/pod_custom_theme.scss',
        ],
    },
    'installable': True,
    'application': True,
}
