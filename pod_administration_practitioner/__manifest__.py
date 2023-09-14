# Copyright 2017 LasLabs Inc.


{
    "name": "Podiatry Administration Practitioner",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, CreuBlanca, LasLabs, "
    "Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/pod_role.xml",
        "views/pod_role.xml",
        "views/res_partner_views.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
