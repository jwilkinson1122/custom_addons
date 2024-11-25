{
    'name': 'Custom module',

    'summary': 'Custom module that alters partner and transfers from'
               ' confirmed sales order.',

    'author': 'Vnikolayev1',

    'category': 'Other Category',
    'license': 'OPL-1',
    'version': '13.0.0.0.0',
    'depends': [
        'base',
        'contacts',
        'sale_management',
        'stock',
        'sale_stock',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/partner_view.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,

}
