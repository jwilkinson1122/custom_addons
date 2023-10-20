{
    "name": "NWPL Base",
    "summary": "Podiatry Base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    'sequence': 1,
    "website": "https://www.nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "base_multi_company",
        "mail", 
        "base_fontawesome", 
        "contacts",
        "knowledge",
        "uom",
        "sale",
        "sale_management",
        'point_of_sale',
        "account",
        "account_accountant",
        "l10n_us",
        "stock",
        "sale_stock",
        "pod_customer_statement",
        "mrp",
        'helpdesk',
        'website_helpdesk_form',
        'website_helpdesk_livechat',
        'helpdesk_repair',
        'helpdesk_stock',
        'helpdesk_mail_plugin',
        'data_merge_helpdesk',
        "mgmtsystem",
        "mgmtsystem_action",
        "mgmtsystem_nonconformity",
        "pod_issue_mgmt",
        "pod_product_issue_mgmt",
        "pod_signature_storage",
        "storage_backend",
        "remote_report_to_printer",
        'web',
        'website',
        'website_sale',
        ],
    "data": [
        "security/pod_security.xml",
        "security/flag_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/pod_practice_type.xml",
        "data/pod_role.xml",
        "views/pod_role.xml",
        "views/pod_diagnosis.xml",
        "views/res_partner.xml",
        "views/pod_menu.xml",
        "views/pod_practice_type.xml",
        "views/pod_patient.xml",
        "views/pod_flag_views.xml",
        "views/pod_flag_category_views.xml",
        "views/res_config_settings_views.xml",
        # "templates/assets.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'pod_base/static/src/scss/main.scss',
            'pod_base/static/src/js/one2many_field.js',
        ],
        
        'web.assets_backend': [
            'pod_base/static/src/css/custom.css',
        ],
    },
    "demo": ["demo/pod_demo.xml"],
    "application": True,
    "installable": True,
    "auto_install": False,
}
