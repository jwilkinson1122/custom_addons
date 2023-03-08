# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Product Configurator",
    'version': '1.0',
    'category': 'Hidden',
    'summary': "Configure your products",

    'description': """
Technical module installed when the user checks the "module_prescription_product_configurator" setting.
The main purpose is to override the sale_order view to allow configuring products in the SO form.

It also enables the "optional products" feature.
    """,

    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/sale_views.xml',
        'wizard/prescription_product_configurator_views.xml',
    ],
    'demo': [
        'data/sale_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale/static/src/js/variant_mixin.js',
            'prescription_product_configurator/static/src/js/product_configurator_renderer.js',
            'prescription_product_configurator/static/src/js/product_configurator_controller.js',
            'prescription_product_configurator/static/src/js/product_configurator_view.js',
            'prescription_product_configurator/static/src/js/product_configurator_widget.js',
            'prescription_product_configurator/static/src/js/product_configurator_modal.js',
        ],
        'web.assets_tests': [
            'prescription_product_configurator/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'prescription_product_configurator/static/tests/product_configurator.test.js',
        ],
    },
    'license': 'LGPL-3',
}
