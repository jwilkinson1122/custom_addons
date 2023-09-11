{
    "name": "Podiatry Quote",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": [
        "nw_pod_careplan_sale", 
        "base_comment_template"
        ],
    "category": "Podiatry",
    "data": [
        "wizards/wizard_create_quote_agreement.xml",
        "views/pod_coverage_agreement.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_quote_views.xml",
        "views/pod_quote_layout_category_views.xml",
        "views/pod_menu.xml",
        "views/product_template_views.xml",
        "reports/pod_quote_templates.xml",
        "reports/pod_quote_report.xml",
        "data/mail_data.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}