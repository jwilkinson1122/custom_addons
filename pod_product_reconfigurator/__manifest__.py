# -*- coding: utf-8 -*-

{
    'name': "Product Reconfigurator",
    'summary': """
        This module allows you to reconfigure a product in sales order
    """,
    'description': """
        This module allows you to reconfigure a product in sales order
    """,
    'author': "RDFlex",
    'company': 'RDFlex',
    'maintainer': 'RDFlex',
    'website': "https://rdflex.com",
    'category': 'Sales',
    'version': '0.1',
    'license': 'OPL-1',
    'depends': ['sale_management'],
    'images': ['static/description/banner.jpg'],
    'data': [
        # 'views/configurate_assets.xml',
        'views/product_configurator_views.xml',
        'views/templates.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "/pod_product_reconfigurator/static/src/js/product_configurator.js",
        ],
    },
}
