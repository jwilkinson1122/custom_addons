

{
    "name": "Podiatry Administration Location",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "license": "LGPL-3",
    "depends": ["podiatry_administration"],
    "data": [
        "security/podiatry_security.xml",
        "data/ir_sequence_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/podiatry_patient.xml",
        "views/podiatry_menu.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "application": False,
}
