{
    "name": "PoS Close approval",
    "version": "15.0.1.0.0",
    "category": "Reporting",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds integration information",
    "depends": ["pos_multiple_sessions", "pos_session_pay_invoice"],
    "post_load": "post_load_hook",
    "data": [
        "security/ir.model.access.csv",
        "wizard/bank_statement_account.xml",
        "views/pos_config_views.xml",
        "views/pos_session_views.xml",
        "views/bank_statement_views.xml",
    ],
}
