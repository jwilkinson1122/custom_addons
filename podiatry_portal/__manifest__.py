{
    "name": "Podiatry Website",
    "description": "Create and check prescription checkout requests.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": [
        "podiatry_checkout",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/podiatry_security.xml",
        "views/main_templates.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "podiatry_portal/static/src/css/podiatry.css",
        }
    },
}
