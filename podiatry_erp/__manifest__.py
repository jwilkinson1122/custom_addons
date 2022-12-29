{
    "name": "Podiatry ERP",
    "version": "15.0.0.0.1",
    "category": "Podiatry",
    'sequence': 1,
    'summary': "Solution for Podiatry clinics",
    'description': """
    odoo Solution for Podiatry clinics.
    """,
    "author": "NWPL",
    "website": "www.nwpodiatric.com",
    'license': 'AGPL-3',
    'images': ['static/description/company_logo.png'],
    "depends": [
        "base_setup",
        "resource",
        "mail",
        "base",
        'sale',
        'sale_management',
        'point_of_sale',
        "product",
        'purchase',
        'stock',
    ],
    "data": [
        'security/groups.xml',
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/product_category.xml",
        "data/sequence.xml",
        "data/podiatry_pos_product_variants.xml",
        "report/reports.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/ophthalmological_prescription_report.xml',
        'report/purchase_order_report.xml',
        'report/sale_order_report.xml',
        'report/invoice_report.xml',
        'views/inherit_sale_order.xml',
        'wizard/complete_pair_order.xml',
        'views/practice.xml',
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
            'podiatry_erp/static/src/css/style.css',
            'podiatry_erp/static/src/lib/base64.js',
            'podiatry_erp/static/src/lib/qrcode.js',
            'podiatry_erp/static/src/js/buttons.js',
            'podiatry_erp/static/src/js/clientListScreen.js',
            'podiatry_erp/static/src/js/models.js',
            'podiatry_erp/static/src/js/OrderReceipt.js',
            'podiatry_erp/static/src/js/popups.js',
            'podiatry_erp/static/src/js/prescriptionPrint.js',
            'podiatry_erp/static/src/js/receiptScreen.js',
            'podiatry_erp/static/src/js/screens.js',
            'podiatry_erp/static/src/js/serializeObject.js',

        ],
        'web.assets_qweb': [
            'podiatry_erp/static/src/xml/**/*',
        ],
    },
    "installable": True,
    'application': True,
}
