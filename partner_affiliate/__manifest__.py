{
    'name': 'Partner Affiliates',
    'version': '17.0.1.1.0',
    'license': 'AGPL-3',
    'depends': ['base', 'web', 'mail', 'web_hierarchy', 'contacts'],
    'data': ['views/res_partner_views.xml'],
    'assets': {
        'web._assets_primary_variables': [
            'partner_affiliate/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'partner_affiliate/static/src/fields/*',
            'partner_affiliate/static/src/views/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}