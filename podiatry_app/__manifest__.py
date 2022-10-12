{
    "name": "Podiatry Management",
    "summary": "Manage podiatry catalog and prescription lending.",
    "author": "NWPL",
    "license": "AGPL-3",
    "website": "https://github.com/PacktPublishing"
               "/Odoo-14-Development-Essentials",
    "version": "14.0.1.0.0",
    "category": "Medical",
    "depends": ["base"],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "views/prescription_view.xml",
        "views/podiatry_menu.xml",
        "views/prescription_list_template.xml",
        "reports/podiatry_prescription_report.xml",
        "reports/podiatry_publisher_report.xml",
    ],
    "demo": [
        "data/res.partner.csv",
        "data/podiatry.prescription.csv",
        "data/prescription_demo.xml",
    ],
    "application": True,
}
