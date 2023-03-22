{
    "name": "Podiatry ERP",
    "version": "15.0.1.0.0",
    "category": "Generic Modules/Base",
    "summary": "Base for custom orthotics manufacturing",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://nwpodiatrtic.com",
    "depends": [
        "account",
        "account_accountant",
        "base",
        "base_setup",
        "contacts",
        'data_merge_helpdesk',
        'helpdesk',
        'website_helpdesk_form',
        'website_helpdesk_livechat',
        'helpdesk_repair',
        'helpdesk_stock',
        'helpdesk_mail_plugin',
        "resource",
        "mail",
        'point_of_sale',
        "product",
        'purchase',
        'sale', 
        'sale_management', 
        'sale_stock',
        'sale_product_configurator',
        'sale_product_matrix',
        'sale_quotation_builder',
        'stock',
    ],
    "data": [
        "security/ir.model.access.csv",
        'data/decimal_precision.xml',
        "data/ir_sequence_data.xml",
        "data/stage_data.xml",
        "wizard/create_prescription_invoice_wizard.xml",
        "wizard/create_prescription_order_wizard.xml",
        "wizard/prescription_mass_message_wizard_view.xml",
        "views/mail_activity_type.xml",
        # 'views/inherit_sale_order.xml',
        "views/podiatry_patient.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_values.xml",
        "views/podiatry_type.xml",
        "views/podiatry_practitioner.xml",
        "views/podiatry_prescription.xml",
        "views/podiatry_prescription_line.xml",
        "views/prescription_kanban_view.xml",
        "views/podiatry_menu.xml",
        "report/report_view.xml",
        "report/patient_card_report.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/pod_prescription_report.xml',
        'report/sale_order_report.xml',
        "report/prescription_demo_report.xml",

    ],
    "assets": {
        "web.assets_backend": [
            "/podiatry/static/src/js/pdf_viewer.js",
        ],
        "point_of_sale.assets": [
            "podiatry/static/src/css/style.css",
            "podiatry/static/src/lib/base64.js",
            "podiatry/static/src/lib/qrcode.js",
            "podiatry/static/src/js/serializeObject.js",
            "podiatry/static/src/js/models.js",
            "podiatry/static/src/js/buttons.js",
            "podiatry/static/src/js/popups.js",
            "podiatry/static/src/js/screens.js",
            "podiatry/static/src/js/clientListScreen.js",
            "podiatry/static/src/js/receiptScreen.js",
            "podiatry/static/src/js/prescriptionPrint.js",
            "podiatry/static/src/js/OrderReceipt.js",
            "podiatry/static/src/lib/qrcode.js",
        ],
        'web.assets_qweb': [
            'podiatry/static/src/xml/pos.xml',
        ],

    },
    "demo": [
        "demo/res_partner_demo.xml",
    ],
    "images": ["static/description/orders.png"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
