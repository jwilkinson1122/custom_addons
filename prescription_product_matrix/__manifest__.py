# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Prescription Matrix",
    'summary': "Add variants to your prescription orders through an Order Grid Entry.",
    'description': """
This module allows to fill Prescription Orders rapidly
by choosing product variants quantity through a Grid Entry.
    """,
    'category': 'Inventory/Prescription',
    'version': '17.0.0.0.0',
    'depends': ['prescription', 'product_matrix'],
    'data': [
        'views/prescription_views.xml',
        'report/prescription_quotation_templates.xml',
        'report/prescription_order_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'prescription_product_matrix/static/src/**/*',
        ],
        'web.assets_tests': [
            'prescription_product_matrix/static/tests/tours/**/*',
        ],
    },
    'license': 'LGPL-3',
}
