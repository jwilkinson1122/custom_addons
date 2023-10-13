{
    "name": "Invoice Integration Email Encrypted",
    "summary": """
        Send invoices through emails as an integration method""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "depends": [
        "edi_account_mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/res_view_value.xml",
        "wizards/res_encrypt_value.xml",
        "views/res_partner_view.xml",
    ],
    "external_dependencies": {"python": ["PyPDF2"], "deb": ["zip"]},
}
