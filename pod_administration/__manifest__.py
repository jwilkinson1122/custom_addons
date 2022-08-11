
{
    "name": "Podiatry Administration",
    "summary": "Podiatry administration base module",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "category": "Medical",
    "license": "LGPL-3",
    "depends": ["pod_base"],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_menu.xml",
        "views/pod_patient_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": True,
}
