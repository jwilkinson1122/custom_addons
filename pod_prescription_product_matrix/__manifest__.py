# -*- coding: utf-8 -*-

{
    'name': "NWPL - Prescription Matrix",
    "author": "NWPL",
    'website': 'https://www.nwpodiatric.com',
    'summary': "Add variants to Prescriptions Order through a grid entry.",
    'description': """Choose product variants quantity through a Grid Entry.""",
    'category': 'Podiatry/Prescriptions',
    'version': '17.0.0.0.0',
    'depends': [
        'pod_prescriptions', 
        'product_matrix', 
        'pod_prescriptions_product_configurator'
        ],
    'data': [
        'views/product_template_views.xml',
        'views/prescriptions_order_views.xml',
        'report/prescriptions_report_templates.xml',
    ],
    'demo': [
        'data/product_matrix_demo.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'pod_prescriptions_product_matrix/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
