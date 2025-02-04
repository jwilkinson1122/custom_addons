# -*- coding: utf-8 -*-

{
    'name': "Partner Organization Chart",
    'version': '17.0.1.0',
    'depends': ['base', 'web', 'mail', 'web_hierarchy', 'contacts'],
    'data': [
        'views/res_partner_views.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [
            'partner_org_chart/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            'partner_org_chart/static/src/fields/*',
            'partner_org_chart/static/src/views/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: