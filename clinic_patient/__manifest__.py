{
    "name": "Clinic Patients",
    "description": "Manage patients receiveing prescriptions.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": ["clinic_app", "mail"],
    "application": False,
    "data": [
        "security/clinic_security.xml",
        "security/ir.model.access.csv",
        "views/prescription_view.xml",
        "views/patient_view.xml",
        "views/clinic_menu.xml",
        "views/prescription_list_template.xml",
    ],
}
