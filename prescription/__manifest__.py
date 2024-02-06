{
    "name": "NWPL Prescription Base",
    "version": "17.0.0.0.0",
    "author": "NWPL",
    "category": "Prescription Management Base",
    "website": "https://nwpodiatric.com",
    "depends": [
        "base", 
        "prescription_theme",
        "prescription_contacts",
        "account",
        "account_accountant",
        "mail", 
        # "portal",
        "l10n_us",
        "sale",
        "sale_management",
        # "sale_product_matrix",
        "stock",
        "sale_stock", 
        "product",
        # "helpdesk",
        # "website_helpdesk_forum",
        # "website_helpdesk_livechat",
        # "helpdesk_repair",
        # "helpdesk_stock",
        # "helpdesk_mail_plugin",
        # "data_merge_helpdesk",
        ],
    "license": "LGPL-3",
    "summary": "Prescription Management to Manage Order and Prescription Configuration",
    "demo": ["demo/prescription_data.xml"],
    "data": [
        "security/prescription_security.xml",
        "security/ir.model.access.csv",
        "data/prescription_sequence.xml",
        "report/report_view.xml",
        "report/prescription_order_report_template.xml",
        "wizard/res_config_settings_views.xml",
        "views/prescription_order.xml",
        "views/prescription_device.xml",
        "views/prescription_device_options.xml",
        "views/prescription_device_type.xml",
        "views/prescription_accommodation_type.xml",
        "views/prescription_accommodations.xml",
        "views/product_product.xml",
        "views/res_company.xml",
        "views/actions.xml",
        "views/menus.xml",
        "wizard/prescription_wizard.xml",
    ],
    "assets": {
        # "web.assets_backend": ["prescription/static/src/css/device_kanban.css"],
        'web.assets_backend': [
            # 'prescription/static/src/scss/prescription_onboarding.scss',
            # 'prescription/static/src/js/prescription_progressbar_field.js',
            # 'prescription/static/src/js/tours/prescription.js',
            'prescription/static/src/js/prescription_product_field.js',
            'prescription/static/src/xml/**/*',
        ],
        'web.assets_frontend': [
            # 'prescription/static/src/scss/prescription_portal.scss',
            # 'prescription/static/src/js/prescription_portal_sidebar.js',
            # 'prescription/static/src/js/prescription_portal_prepayment.js',
            # 'prescription/static/src/js/prescription_portal.js',
        ],
        'web.assets_tests': [
            # 'prescription/static/tests/tours/**/*',
        ],
        'web.qunit_suite_tests': [
            'prescription/static/tests/**/*',
            # ('remove', 'prescription/static/tests/tours/**/*')
        ],
    },
    "external_dependencies": {"python": ["python-dateutil"]},
    # "images": ["static/description/Prescription.png"],
    "application": True,
    "installable": True,
}
