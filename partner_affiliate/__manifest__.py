{
    'name': 'Partner Affiliates',
    'version': '17.0.1.1.0',
    'license': 'AGPL-3',
    'depends': [
        'base', 
        'base_setup',
        'web', 
        'mail', 
        'web_hierarchy', 
        'account',
        'contacts', 
        # 'pod_web_chatter',
        'sales_team',
        'sale',
        'sale_management',
        'product',

        ],
    'data': [
        'security/ir.model.access.csv', 
        'views/res_partner_views.xml'
        ],
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