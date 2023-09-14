

{
    "name": "Account Credit Control Deferred",
    "summary": """
        Defferred credit control mails""",
    "version": "15.0.1.1.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["account_credit_control"],
    "data": [
        "views/res_company.xml",
        "reports/report_credit_control_summary.xml",
        "views/credit_control_line.xml",
        "views/credit_control_communication.xml",
        "views/res_partner.xml",
    ],
    "post_init_hook": "post_init_hook",
}
