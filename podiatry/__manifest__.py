# See LICENSE file for full copyright and licensing details.

{
    "name": "Podiatry ERP",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "http://www.nwpodiatric.com",
    "category": "Podiatry Management",
    "license": "AGPL-3",
    "Summary": "A Module For Podiatry Management",
    "depends": [
        "account",
        "account_accountant",
        "account_reports",
        "l10n_us",
        "base",
        "base_setup",
        "contacts",
        "crm", 
        "hr",
        "mail",
        "sale",
        "sale_management",
        "stock"
        
        ],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/patient_sequence.xml",
        "data/mail_template.xml",
        "wizard/close_reason_view.xml",
        "views/patient_view.xml",
        "views/podiatry_view.xml",
        "views/practitioner_view.xml",
        "views/doctor_view.xml",
        "wizard/assign_roll_no_wizard.xml",
        "wizard/move_standards_view.xml",
        "report/report_view.xml",
        "report/identity_card.xml",
        "report/practitioner_identity_card.xml",
    ],
    "demo": ["demo/podiatry_demo.xml"],
    "assets": {
        "web.assets_backend": ["/podiatry/static/src/scss/podiatrycss.scss"]
    },
    "installable": True,
    "application": True,
}
