# -*- coding: utf-8 -*-

{
    "name": "NWPL Custom Orthotics Manufacturing System",
    "author": "NWPL",
    "version": "17.0.0.0.0",
    "depends": [
        "account",
        "contacts",
        "base",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/res_partner_change_parent.xml",
        "views/res_partner_view.xml",
        "data/ir_cron.xml",
    ],
    "demo": ["demo/ir_ui_view.xml"],
    "assets": {},
    "images": ["static/description/icon.png"],
    "external_dependencies": {"python": ["astor"]},
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
    "installable": True,
}
