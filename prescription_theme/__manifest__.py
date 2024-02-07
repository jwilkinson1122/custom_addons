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
            '/prescription_theme/static/src/scss/prescription_theme.scss',
        ],
    },
    'installable': True,
    'application': True,
}
