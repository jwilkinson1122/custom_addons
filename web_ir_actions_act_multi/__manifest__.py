{
    "name": "Web Actions Multi",
    "summary": "Enables triggering of more than one action on ActionManager",
    "category": "Web",
    "version": "15.0.1.0.0",
    "license": "LGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["web"],
    "data": ["security/ir.model.access.csv"],
    "assets": {
        "web.assets_backend": [
            "web_ir_actions_act_multi/static/src/**/*.esm.js",
        ],
    },
    "installable": True,
}
