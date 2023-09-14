{
    "name": "Document Quick Access Label",
    "summary": """
        Allows to print labels from Document Quick Access records""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "document_quick_access",
        "printer_zpl2",
        "remote_report_to_printer_label",
    ],
    "data": ["views/document_quick_access_rule.xml"],
}
