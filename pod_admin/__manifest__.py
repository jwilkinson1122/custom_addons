

{
    "name": "Podiatry Administration",
    "summary": "Podiatry administration base module",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Podiatry",
    "license": "LGPL-3",
    "depends": ["podiatry_base"],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/res_partner.xml",
        "views/podiatry_menu.xml",
        "views/podiatry_patient_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/podiatry_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": True,
}
