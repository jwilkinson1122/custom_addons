{
    "name": "POS Session Pay invoice",
    "version": "15.0.1.0.1",
    "category": "Point Of Sale",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "summary": "Pay and receive invoices from PoS Session",
    "license": "LGPL-3",
    "depends": ["point_of_sale", "account_cash_invoice"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/pos_box_cash_invoice_out.xml",
        "wizard/pos_box_cash_invoice_in.xml",
        "wizard/cash_invoice_in.xml",
        "views/pos_session.xml",
    ],
}
