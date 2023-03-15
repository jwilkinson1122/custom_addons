 

{
    "name": "Podiatry Base",
    "summary": "Podiatry Base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["mail", "base_fontawesome", "uom"],
    "data": [
        "security/podiatry_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "data/ir_sequence_data.xml",
        "views/podiatry_menu.xml",
        "views/podiatry_patient.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/podiatry_demo.xml"],
    "application": True,
}
