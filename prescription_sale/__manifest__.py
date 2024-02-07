 
{
    'name': 'NWPL - Prescription Link with Sales',
    'summary': 'Sale Order - Prescription',
    'version': '17.0.0.0.0',
    'category': 'Prescription',
    'website': 'https://www.nwpodiatric.com',
    'author': 'NWPL',
    'license': 'LGPL-3',
    "depends": [
        "prescription", 
        "sale_stock"
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/report_prescription.xml',
        'views/prescription_views.xml',
        'views/sale_views.xml',
        'views/sale_portal_template.xml',
        'views/res_config_settings_views.xml',
        'views/prescription_type_views.xml',
        'wizard/sale_order_prescription_wizard_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/prescription_sale/static/src/js/prescription_portal_form.js',
            '/prescription_sale/static/src/scss/prescription_sale.scss',
        ],
        'web.assets_tests': [
            '/prescription_sale/static/src/tests/*.js',
        ],
    },

    'installable': True,
    'application': False,
}

