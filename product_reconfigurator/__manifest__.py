# -*- coding: utf-8 -*-

{
    'name': "Product Reconfigurator",
    'summary': """
        This module allows you to reconfigure a product in sales order
    """,
    'description': """
        This module allows you to reconfigure a product in sales order
    """,
    'author': "NWPL",
    'website': "https://www.nwpodiatric.com",
    'category': 'Sales',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_management', 
        'sale_product_configurator',
        ],
    'data': [
        # 'views/configurate_assets.xml',
        'views/product_configurator_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_reconfigurator/static/src/js/product_configurator.js',
        ],
    },
}
