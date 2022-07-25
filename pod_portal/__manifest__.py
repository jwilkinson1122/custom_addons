{
    "name": "Podiatry Website",
    "description": "Create and check prescription bookout requests.",
    "author": "NWPL",
    "license": "AGPL-3",
    "depends": [
        "pod_bookout",
        "portal",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/pod_security.xml",
        "views/main_templates.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "pod_portal/static/src/css/pod.css",
        }
    },
}
