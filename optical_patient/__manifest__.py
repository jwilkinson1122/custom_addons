{
    "name": "Patient",
    "version": "1.0",
    "category": "setting",
    "license": "OPL-1",
    "images": ["static/description/dr.jpg"],
    "depends": [
        "base",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "view/user_creation_wizard.xml",
        "view/patient.xml",
    ],
    "installable": True,
}
