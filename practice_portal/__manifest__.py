{
    "name": "Practice Website",
    "description": "Create and check prescription bookout requests.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": [
        "practice_bookout",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/practice_security.xml",
        "views/main_templates.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "practice_portal/static/src/css/practice.css",
        }
    },
}
