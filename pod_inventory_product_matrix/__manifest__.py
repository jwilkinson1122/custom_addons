# -*- coding: utf-8 -*-
{
    "name": "Inventory Product Matrix",
    'summary': """Customize your Odoo Inventory picking product document selection view with multiple layouts.""",
    "description": """ """,
    "license": "AGPL-3",
    "category": "Inventory",
    'version': "18.0.0.1",
    'sequence': 0,
    "depends": ['base', 'stock', 'product', 'product_matrix'],
    "data": [
        'views/stock_picking_views.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
        'report/stock_picking_operations.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pod_inventory_product_matrix/static/src/**/*.js',
            'pod_inventory_product_matrix/static/src/scss/product_matrix.scss',
            'pod_inventory_product_matrix/static/src/**/*.xml',
        ],
    },
    "installable": True,
    'application': True,
    "auto_install": False,
}