# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'POS - Prescriptions',
    'version': '17.0.0.0.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'Link module between Point of Sale and Prescriptions',
    'description': """

This module adds a custom Sales Team for the Point of Sale. This enables you to view and manage your point of sale sales with more ease.
""",
    'depends': ['point_of_sale', 'prescription_management'],
    'data': [
        'data/pos_prescription_data.xml',
        'security/pos_prescription_security.xml',
        'security/ir.model.access.csv',
        'views/point_of_sale_report.xml',
        'views/prescription_order_views.xml',
        'views/pos_order_views.xml',
        'views/prescription_team_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_template.xml',
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_prescription/static/src/**/*',
        ],
        'web.assets_tests': [
            'pos_prescription/static/tests/**/*',
        ],
    },
    'license': 'LGPL-3',
}
