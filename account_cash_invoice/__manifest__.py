{
    "name": "Account cash invoice",
    "version": "15.0.1.3.0",
    "category": "Accounting",
    "author": "NWPL",
    "website": "https://github.com/OCA/account-payment",
    "summary": "Pay and receive invoices from bank statements",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/cash_invoice_out.xml",
        "wizard/cash_invoice_in.xml",
    ],
}
