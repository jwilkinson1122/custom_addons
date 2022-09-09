{
    "name": "Practice Practitioners",
    "description": "Manage practitioners borrowing prescriptions.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["practice_app", "mail"],
    "application": False,
    "data": [
        "security/practice_security.xml",
        "security/ir.model.access.csv",
        "views/prescription_view.xml",
        "views/practitioner_view.xml",
        "views/practice_menu.xml",
        "views/prescription_list_template.xml",
    ],
}
