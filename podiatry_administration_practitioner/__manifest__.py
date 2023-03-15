 
{
    "name": "Podiatry Administration Practitioner",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": ["podiatry_base"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/podiatry_role.xml",
        "views/podiatry_role.xml",
        "views/res_partner_views.xml",
        "views/podiatry_menu.xml",
    ],
    "demo": ["demo/podiatry_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
