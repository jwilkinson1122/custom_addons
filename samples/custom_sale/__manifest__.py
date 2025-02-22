{
    'name': 'Custom Sale',
    'version': '1.0',
    'summary': 'Odoo 18 sales module customizations',
    'depends': ['web', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_sale/static/src/**/*'
        ]
    },
    
    'installable': True,
    'application': False,
    'license': 'LGPL-3'
}
