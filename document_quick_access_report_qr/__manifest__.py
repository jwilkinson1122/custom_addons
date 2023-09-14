{
    "name": "Document Quick Access Report Qr",
    "summary": """
        Add QR to models reports""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "document_quick_access",
        "account_banking_sepa_direct_debit",
        "report_qr",
        "sale",
    ],
    "data": [
        "report/report_invoice.xml",
        "report/sale_report_templates.xml",
        "report/sepa_direct_debit_mandate.xml",
    ],
}
