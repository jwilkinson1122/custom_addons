{
    "name": "Podiatry Patients",
    "description": "Manage patients prescriptions.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["pod_app", "mail"],
    "application": False,
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/prescription_view.xml",
        "views/patient_view.xml",
        "views/pod_menu.xml",
        "views/prescription_list_template.xml",
    ],
}
