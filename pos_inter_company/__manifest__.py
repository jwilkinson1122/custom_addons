{
    "name": "Cash payments between intercompanies",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "summary": "Payment of invoices to another company",
    "sequence": 30,
    "category": "Accounting",
    "depends": [
        "pos_session_pay_invoice",
        "account_journal_inter_company",
        "pos_close_approval",
    ],
    "license": "AGPL-3",
    "data": [
        "views/account_bank_statement_line.xml",
        "views/pos_session.xml",
        "wizard/cash_invoice_in.xml",
        "wizard/cash_invoice_out.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
