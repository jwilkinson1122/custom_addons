# -*- coding: utf-8 -*-
{
    "name": "NWPL - PoS Multiple Shops",
    "version": "17.0.0.0.0",
    "category": "Point of Sale",
    "depends": [
        'base', 
        'sale', 
        'point_of_sale',
        
        ],
    "author": "NWPL",
    'summary': 'app Multiple shop in Point of Sale point of sales',
    "description": """PoS Multiple shop management""",
    "website": "https://www.nwpodiatric.com",
    "data": [
        'security/ir.model.access.csv',
        'views/pos_shop_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_multi_shop/static/src/js/models.js',
            'pos_multi_shop/static/src/js/ProductsWidget.js',
        ],
    },
    "auto_install": False,
    "installable": True,
    "images": ['static/description/icon.png'],
    'license': 'OPL-1',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
