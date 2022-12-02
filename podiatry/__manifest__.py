{
    "name": "Podiatry Manager",
    "version": "15.0.1.0",
    "category": "Health Care/Health Care",

    "summary": "podiatry practice, practitioner, patient and prescription information",
    "author": "NWPL",

    "website": "https://nwpodiatric.com",
    "license": "GPL-3",

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

        # "contacts",
    ],

    "data": [
        # ----
        # Data
        # ====
        "data/data.xml",
        "data/ir_sequence_data.xml",
        "data/ir_module_category_data.xml",
        "data/stage_data.xml",
        "data/product_category.xml",
        "data/pos_product_variants.xml",
        # --------
        # Security
        # ========
        "security/res_groups_data.xml",
        "security/ir_model_access_data.xml",
        "security/ir.model.access.csv",
        # 'security/ir.model.access.csv',
        # -------
        # Wizards
        # =======
        "wizard/create_prescription_invoice_wizard.xml",
        "wizard/create_prescription_shipment_wizard.xml",
        "wizard/prescription_mass_message_wizard_view.xml",
        'wizard/complete_pair_order.xml',
        # -----
        # Views
        # =====
        "views/podiatry_root.xml",
        "views/res_config_settings.xml",
        "views/mail_activity_type.xml",
        "views/podiatry_patient.xml",
        "views/pos_variants.xml",
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
        'views/pos_customer_favorites_view.xml',
        "views/podiatry_patient_shoe_size.xml",
        "views/podiatry_patient_shoe_width.xml",
        "views/podiatry_patient_diagnosis.xml",
        "views/podiatry_patient_weight.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_type.xml",
        "views/podiatry_practitioner.xml",
        "views/podiatry_menu.xml",
        "views/podiatry_prescription.xml",
        "views/podiatry_prescription_line.xml",
        "views/prescription_kanban_view.xml",
        'views/product_attribute_view.xml',
        'views/view.xml',
        "data/stage_data.xml",
        "views/podiatry_specialty.xml",
        "views/res_partner.xml",
        # -------
        # Reports
        # =======
        "report/report_view.xml",
        "report/patient_card_report.xml",
        "report/prescription_demo_report.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/pod_prescription_report.xml',
        'report/purchase_order_report.xml',
        'report/sale_order_report.xml',
        'report/invoice_report.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_product_template.xml',
        'views/inherit_invoice.xml',

    ],

    'assets': {
        'point_of_sale.assets': [
            # 'podiatry/static/src/css/pos.css',
            'podiatry/static/src/css/style.css',
            'podiatry/static/lib/JsBarcode.all.min.js',
            'podiatry/static/lib/base64.min.js',
            'podiatry/static/lib/qrcode.min.js',
            'podiatry/static/src/js/Barcode.js',
            'podiatry/static/src/js/Qrcode.js',
            # 'podiatry/static/src/js/AmountInWords.js',
            'podiatry/static/src/js/OrderReceipt.js',
            # 'podiatry/static/src/js/OrderReceiptA4.js',
            'podiatry/static/src/js/PrescriptionPrint.js',
            'podiatry/static/src/js/ReceiptScreen.js',
            'podiatry/static/src/js/Buttons.js',
            "podiatry/static/src/js/ClientDetailsEdit.js",
            "podiatry/static/src/js/ClientListScreen.js",
            "podiatry/static/src/js/models.js",
            'podiatry/static/src/js/PosImageField.js',
            'podiatry/static/src/js/PosReceiptImage.js',
            'podiatry/static/src/js/main.js',
            'podiatry/static/src/css/label.css',
            'podiatry/static/src/js/models.js',
            'podiatry/static/src/js/serializeObject.js',
            'podiatry/static/src/js/ProductPopup.js',
            'podiatry/static/src/js/ProductScreen.js',
        ],
        'web.assets_backend': [
            # 'podiatry/static/src/scss/podiatry_practice.scss',
            # 'podiatry/static/src/scss/card.scss',
            # 'podiatry/static/src/css/customerscreen.css',
            # 'podiatry/static/src/css/label.css',
            # 'podiatry/static/src/css/main.css',
        ],
        'web.assets_qweb': [
            'podiatry/static/src/xml/**/*',
        ],
    },
    # "demo": ["demo/res_partner.xml", "demo/ir_actions.xml"],
    "demo": ['data/pos_customer_favorites_demo.xml'],
    "installable": True,
    "application": True,
}
