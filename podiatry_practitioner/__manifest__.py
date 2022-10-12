{
    "name": "Podiatry Practitioners",
    "description": "Manage practitioners prescriptions.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["podiatry_app", "mail"],
    "application": False,
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "views/prescription_view.xml",
        "views/practitioner_view.xml",
        "views/podiatry_menu.xml",
        "views/prescription_list_template.xml",
    ],
}
