# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Administration Practitioner",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, CreuBlanca, LasLabs, "
    "Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/podiatry-fhir",
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
