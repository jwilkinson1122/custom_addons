{
    "name": "Podiatry ERP",
    "version": "15.0.0.0.1",
    "category": "Podiatry",
    'sequence': 1,
    'summary': "Solution for manufacturing custom medical devices",
    'description': """
    Solution for manufacturing custom medical devices.
    """,
    "author": "NWPL",
    "website": "www.nwpodiatric.com",
    'license': 'AGPL-3',
    'images': [],
    "depends": [
        'base', 'sale', 'purchase',
    ],
    "data": [
        'security/groups.xml',
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/data.xml",
        "data/product_category.xml",
        "data/sequence.xml",
        "report/reports.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/medical_prescription_report.xml',
        'report/purchase_order_report.xml',
        'report/sale_order_report.xml',
        'report/invoice_report.xml',
        'views/inherit_sale_order.xml',
        'wizard/complete_pair_order.xml',
        'views/doctor.xml',
        'views/doctor_wizard.xml',
        "views/prescription.xml",
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

        ],
        'web.assets_qweb': [
        ],
    },
    "installable": True,
    'application': True,
}
