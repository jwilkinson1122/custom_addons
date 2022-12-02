{
    "name": "Optical ERP",
    "version": "15.0.0.0.1",
    "category": "Optical",
    'sequence': 1,
    'live_test_url': 'https://youtu.be/EKacxPASgWc',
    'summary': "Solution for Optical(EYE) shops and clinics",
    'description': """
    odoo Solution for Optical(EYE) shops and clinics.
    """,
    "author": "Alhaditech",
    "website": "www.alhaditech.com",
    'license': 'AGPL-3',
    'images': ['static/description/background.png', 'static/description/background2.png'],
    "depends": [
        'base', 'sale', 'sale_management', 'product', 'point_of_sale', 'purchase',
    ],
    'price': 148, 'currency': 'USD',
    "data": [
        'security/groups.xml',
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/product_category.xml",
        "data/sequence.xml",
        "data/optical_pos_product_variants.xml",
        "report/reports.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/ophthalmological_prescription_report.xml',
        'report/purchase_order_report.xml',
        'report/sale_order_report.xml',
        'report/invoice_report.xml',
        'views/inherit_sale_order.xml',
        'wizard/complete_pair_order.xml',
        'views/doctor.xml',
        'views/patient.xml',
        'views/doctor_wizard.xml',
        "views/prescription.xml",
        'views/pos_order_view.xml',
        "views/res_config_settings_views.xml",
        "views/partner.xml",
        "views/test_type.xml",
        'views/product_attribute_view.xml',
        'views/view.xml',
        'views/inherit_product_template.xml',
        'views/inherit_invoice.xml',
    ],
    "assets": {
        "point_of_sale.assets": [
            'optical_erp/static/src/css/style.css',
            'optical_erp/static/src/lib/base64.js',
            'optical_erp/static/src/lib/qrcode.js',
            'optical_erp/static/src/js/buttons.js',
            'optical_erp/static/src/js/clientListScreen.js',
            'optical_erp/static/src/js/models.js',
            'optical_erp/static/src/js/OrderReceipt.js',
            'optical_erp/static/src/js/popups.js',
            'optical_erp/static/src/js/prescriptionPrint.js',
            'optical_erp/static/src/js/receiptScreen.js',
            'optical_erp/static/src/js/screens.js',
            'optical_erp/static/src/js/serializeObject.js',

        ],
        'web.assets_qweb': [
            'optical_erp/static/src/xml/**/*',
        ],
    },
    "installable": True,
    'application': True,
}
