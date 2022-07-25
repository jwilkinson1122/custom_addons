{
    "name": "Clinic Website",
    "description": "Create and check prescription bookout requests.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": [
        "clinic_bookout",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/clinic_security.xml",
        "views/main_templates.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "clinic_portal/static/src/css/clinic.css",
        }
    },
}
