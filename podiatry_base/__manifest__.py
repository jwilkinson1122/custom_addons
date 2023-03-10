# Copyright 2017-2022 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Base",
    "summary": "Podiatry Base",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, Eficent, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/podiatry-fhir",
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
