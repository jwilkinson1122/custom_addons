# -*- coding: utf-8 -*-

{
    'name': "NWPL Prescription Matrix",
    "author": "NWPL",
    'summary': "Add variants to Prescription Order through a grid entry.",
    'description': """
This module allows to fill Prescription Order rapidly
by choosing product variants quantity through a Grid Entry.
    """,
    'category': 'Podiatry/Prescription',
    'version': '1.0',
    'depends': [
        'prescription', 
        'product_matrix', 
        'prescription_product_configurator'
        ],
    'data': [
        'views/product_template_views.xml',
        'views/prescription_order_views.xml',
        'report/prescription_report_templates.xml',
    ],
    'demo': [
        'data/product_matrix_demo.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'prescription_product_matrix/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
