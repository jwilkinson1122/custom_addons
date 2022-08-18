
{
    "name": "Podiatry Practice",
    "summary": "Add Summary Here",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_administration", "pod_administration_location"],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/pod_contact_view.xml",
        "views/pod_menu.xml",
        "views/pod_patient.xml",
        "security/ir.model.access.csv",
        "data/pod_contact_sequence.xml",
    ],
    "installable": True,
    "auto_install": False,
}
