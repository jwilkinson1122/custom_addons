# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Administration Location",
    "version": "15.0.1.0.0",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "author": "LasLabs, CreuBlanca, ForgeFlow,"
    "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["pod_base"],
    "data": [
        "data/ir_sequence_data.xml",
        "views/res_partner_views.xml",
        "views/pod_patient.xml",
        "views/pod_menu.xml",
    ],
    "demo": ["demo/res_partner_demo.xml"],
    "installable": True,
    "application": False,
}
