# See LICENSE file for full copyright and licensing details.

{
    "name": "Podiatry ERP - Accounts",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "http://www.nwpodiatric.com",
    "category": "Podiatry Management",
    "license": "AGPL-3",
    "summary": "A Module For Podiatry ERP Accounts Management",
    "depends": ["podiatry"],
    # "images": ["static/description/PodiatryAccounts.png"],
    "data": [
        "security/ir.model.access.csv",
        "security/security_accounts.xml",
        "data/podiatry_accounts_sequence.xml",
        "data/mail_template.xml",
        "data/data.xml",
        "views/podiatry_accounts_view.xml",
        # "report/patient_payslip.xml",
        "report/patient_accounts_register.xml",
        "report/report_view.xml",
    ],
    "demo": ["demo/podiatry_accounts_demo.xml"],
    "installable": True,
    "application": True,
}
