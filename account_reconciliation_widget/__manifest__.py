{
    "name": "account_reconciliation_widget",
    "version": "15.0.1.2.9",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Account reconciliation widget",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["account"],
    "development_status": "Production/Stable",
    "data": [
        "security/ir.model.access.csv",
        "wizards/res_config_settings_views.xml",
        "views/account_view.xml",
        "views/account_bank_statement_view.xml",
        "views/account_journal_dashboard_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_reconciliation_widget/static/src/scss/account_reconciliation.scss",
            "account_reconciliation_widget/static/src/js/reconciliation/**/*",
        ],
        "web.qunit_suite_tests": [
            "account_reconciliation_widget/static/tests/**/*",
        ],
        "web.assets_qweb": [
            "account_reconciliation_widget/static/src/xml/account_reconciliation.xml",
        ],
    },
    "installable": True,
}
