

{
    "name": "Pod Administration Practitioner",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["pod_administration"],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/pod_role.xml",
        "views/res_config_settings_views.xml",
        "views/pod_role.xml",
        "views/res_partner_views.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
