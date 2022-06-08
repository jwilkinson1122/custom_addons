

{
    "name": "Pod Administration Location",
    "version": "15.0.1.0.0",
    "category": "Medical",
    "website": "https://nwpodiatric.com",
    "author": "LasLabs, Creu Blanca, Eficent,"
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["pod_administration"],
    "data": [
        "security/pod_security.xml",
        "data/ir_sequence_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/pod_location_relationship.xml",
        "views/pod_patient.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "application": False,
}
