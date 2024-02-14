# -*- coding: utf-8 -*-

{
    'name': "NWPL - Prescription Matrix",
    "author": "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'summary': "Add variants to Prescription Order through a grid entry.",
    'description': """Choose product variants quantity through a Grid Entry.""",
    'category': 'Podiatry/Prescription',
    'version': '17.0.0.0.0',
    'depends': [
        'pod_prescription', 
        'product_matrix', 
        'pod_prescription_product_configurator'
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
            'pod_prescription_product_matrix/static/src/**/*',
        ],
    },
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
}
