# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Administration Encounter",
    "summary": "Add Encounter concept",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Podiatry",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": ["pod_administration_location"],
    "data": [
        "security/ir.model.access.csv",
        "views/pod_encounter_view.xml",
        "views/pod_menu.xml",
        "views/pod_patient.xml",
        "security/ir.model.access.csv",
        "data/pod_encounter_sequence.xml",
    ],
    "demo": [
        "demo/data.xml",
    ],
    "installable": True,
    "auto_install": False,
}
