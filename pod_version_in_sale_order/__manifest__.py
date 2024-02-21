
{
    'name': 'NWPL - Sale Order Versions',
    'version': '17.0.0.0.0',
    'category': 'Sales/Sales',
    'summary': 'For creating multiple sale order versions',
    'description': 'For creating multiple sale order versions',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'images': ['static/description/icon.png'],
    'depends': [
        'base', 
        'sale_management'
        ],
    'data': [
        'views/sale_order.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
