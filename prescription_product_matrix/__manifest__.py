# -*- coding: utf-8 -*-

{
    'name': 'NWPL - Product Matrix',
    'summary': 'Add variants to Prescription Order through a grid entry.',
    'category': 'Podiatry/Prescription',
    'author': 'NWPL',
    'website': 'https://www.nwpodiatric.com',
    'version': '17.0.0.0.0',
    'depends': [
        'prescription', 
        'product_matrix', 
        'prescription_product_configurator'
        ],
    'data': [
        'views/product_template_views.xml',
        'views/prescription_views.xml',
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
    'auto_install': True,
    'license': 'LGPL-3',
}
