# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Encounter careplan",
    "summary": "Joins careplans and encounters",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/pod-fhir",
    "category": "Podiatry",
    "license": "LGPL-3",
    "depends": [
        "pod_administration_encounter",
        "pod_clinical_careplan",
    ],
    "data": [
        "views/pod_encounter_view.xml",
        "views/pod_request_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
