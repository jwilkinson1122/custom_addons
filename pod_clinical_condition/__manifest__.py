# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Condition",
    "summary": "Podiatry condition",
    "version": "15.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/pod-fhir",
    "license": "LGPL-3",
    "depends": [
        "pod_terminology_sct",
        "pod_administration_encounter",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_patient_views.xml",
        "views/pod_encounter_views.xml",
        "views/pod_condition_views.xml",
        "views/pod_clinical_finding_views.xml",
        "views/pod_allergy_substance_views.xml",
    ],
    "demo": ["demo/pod_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
