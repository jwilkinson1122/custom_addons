{
    "name": "Podiatry ERP",
    "version": "15.0.1.0.0",
    "category": "Medical",
    "summary": "Base for custom orthotics manufacturing",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://nwpodiatrtic.com",
    "depends": [
        "contacts",
        "account",
        "account_accountant",
        "l10n_us",
        "base",
        "base_setup",
        # "base_multi_company",
        "resource",
        "mail",
        'helpdesk',
        'website_helpdesk_form',
        'website_helpdesk_livechat',
        'helpdesk_repair',
        'helpdesk_stock',
        'helpdesk_mail_plugin',
        'data_merge_helpdesk',
        'sale',
        'sale_management',
        'mrp',
        'point_of_sale',
        "product",
        'purchase',
        'sale_stock',
        'stock',
        'web',
        'website',
        'website_sale',
        
    ],
    "data": [
        'security/podiatry_security.xml',
        "security/ir.model.access.csv",
        # "views/res_config_settings_view.xml",
        "data/product_category.xml",
        'data/decimal_precision.xml',
        "data/ir_sequence_data.xml",
        # 'data/mail_template_data.xml',
        "data/podiatry_practice_type.xml",
        'data/podiatry_role.xml',
        "data/stage_data.xml",
        # 'views/s3_views.xml',
        'views/product_template.xml',
        "views/product_view.xml",
        "wizard/create_prescription_invoice_wizard.xml",
        "wizard/create_prescription_shipment_wizard.xml",
        "wizard/prescription_mass_message_wizard_view.xml",
        # 'wizard/select_products_wizard_view.xml',
        "views/mail_activity_type.xml",
        'views/inherit_sale_order.xml',
        "views/podiatry_patient.xml",
        "views/podiatry_practice.xml",
        "views/podiatry_practice_type.xml",
        "views/podiatry_values.xml",
        "views/podiatry_type.xml",
        "views/podiatry_practitioner.xml",
        'views/podiatry_role.xml',
        "views/podiatry_prescription.xml",
        "views/prescription_kanban_view.xml",
        'views/configuration_view.xml',
        # 'views/inherit_product_template.xml',
        # 'views/res_partner.xml',
        "views/podiatry_menu.xml",
        'views/podiatry_specialty.xml',
        "report/report_view.xml",
        "report/patient_card_report.xml",
        "report/ticket_report_format.xml",
        "report/prescription_report.xml",
        'report/pod_prescription_report.xml',
        'report/sale_order_report.xml',
        'views/res_user.xml',
        'wizard/mail_compose_view.xml',
        'wizard/customer_statement_mass_action.xml',
        'wizard/customer_config_update_wizard.xml',
        'views/mail_history.xml',
        'views/res_config_settings_view.xml',
        # 'views/mail_history.xml',
        # 'views/res_config_settings_view.xml',
        'views/res_partner.xml',
        'views/customer_statement_menu.xml',
        'report/customer_statement_report.xml',
        'report/customer_due_statement_report.xml',
        'report/customer_filter_statement_report.xml',
        'data/email_data.xml',
        'data/statement_cron.xml',
        'views/customer_statement_portal_templates.xml',
    ],
    "assets": {
        'web.assets_frontend': [
            'podiatry/static/src/js/portal.js',
        ],
        "web.assets_backend": [
            "podiatry/static/src/css/main.css",
            "podiatry/static/src/js/pdf_viewer.js",
            # "podiatry/static/src/js/float_with_uom.js",
            
        ],
        'web.assets_qweb': [
            'podiatry/static/src/xml/pos.xml',
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


    },
    "demo": [
        "demo/res_partner_demo.xml",

    ],
    # "external_dependencies": {"python": ["boto3"]},
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "images": ["static/description/orders.png"],
    "development_status": "Beta",
    "maintainers": ["NWPL"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
